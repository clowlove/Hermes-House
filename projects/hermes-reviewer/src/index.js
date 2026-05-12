/**
 * Hermès Reviewer - GitHub App
 * AI-powered automated code review for pull requests
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration from environment
const APP_ID = process.env.GITHUB_APP_ID;
const PRIVATE_KEY = process.env.GH_APP_PRIVATE_KEY?.replace(/\\n/g, '\n');
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;
const MODEL_BASE_URL = process.env.MODEL_BASE_URL || 'https://integrate.api.nvidia.com/v1';
const MODEL_API_KEY = process.env.MODEL_API_KEY;

/**
 * Generate JWT for GitHub App authentication
 */
function generateJWT() {
  const jwt = require('jsonwebtoken');
  const now = Math.floor(Date.now() / 1000);
  
  const payload = {
    iat: now,
    exp: now + 600, // 10 minutes
    iss: APP_ID
  };
  
  return jwt.sign(payload, PRIVATE_KEY, { algorithm: 'RS256' });
}

/**
 * Get installation access token
 */
async function getInstallationToken(installationId) {
  const jwt = generateJWT();
  
  const response = await fetch(
    `https://api.github.com/app/installations/${installationId}/access_tokens`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${jwt}`,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
      }
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to get installation token: ${response.status}`);
  }
  
  const data = await response.json();
  return data.token;
}

/**
 * Analyze code changes using AI
 */
async function analyzeCodeChanges(prData, installationId) {
  const prompt = `You are a senior code reviewer. Analyze this pull request:

Title: ${prData.title}
Description: ${prData.body || 'No description provided'}

Files changed:
${prData.files.map(f => `${f.filename} (+${f.additions} -${f.deletions})`).join('\n')}

Review the code and provide:
1. Overall assessment (1-2 sentences)
2. Potential issues (bulleted list, max 3)
3. Suggestions for improvement (bulleted list, max 3)
4. Security concerns if any (bulleted list, max 2)

Be concise and actionable. Focus on the most important feedback.`;

  try {
    const response = await fetch(`${MODEL_BASE_URL}/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${MODEL_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'meta/llama-3.1-8b-instruct',
        prompt: prompt,
        max_tokens: 500,
        temperature: 0.3
      })
    });
    
    if (!response.ok) {
      console.error('AI API error:', response.status);
      return {
        assessment: '⚠️ AI review temporarily unavailable. Please review manually.',
        issues: [],
        suggestions: [],
        security: []
      };
    }
    
    const data = await response.json();
    return parseAIResponse(data.choices?.[0]?.text || '');
  } catch (error) {
    console.error('AI analysis error:', error);
    return {
      assessment: '⚠️ AI review failed. Please review manually.',
      issues: [],
      suggestions: [],
      security: []
    };
  }
}

/**
 * Parse AI response into structured format
 */
function parseAIResponse(text) {
  const sections = {
    assessment: '',
    issues: [],
    suggestions: [],
    security: []
  };
  
  let currentSection = 'assessment';
  
  text.split('\n').forEach(line => {
    const lowerLine = line.toLowerCase();
    if (lowerLine.includes('overall') || lowerLine.includes('assessment')) {
      currentSection = 'assessment';
    } else if (lowerLine.includes('issue') || lowerLine.includes('problem')) {
      currentSection = 'issues';
    } else if (lowerLine.includes('suggestion') || lowerLine.includes('improve')) {
      currentSection = 'suggestions';
    } else if (lowerLine.includes('security')) {
      currentSection = 'security';
    } else if (line.trim().startsWith('-') || line.trim().startsWith('*')) {
      const content = line.trim().substring(1).trim();
      if (content) {
        sections[currentSection].push(content);
      }
    } else if (line.trim() && currentSection === 'assessment') {
      sections.assessment += line.trim() + ' ';
    }
  });
  
  sections.assessment = sections.assessment.trim();
  
  return sections;
}

/**
 * Post review comment to PR
 */
async function postReviewComment(owner, repo, prNumber, review) {
  const installationId = parseInt(process.env.INSTALLATION_ID || '0');
  const token = await getInstallationToken(installationId);
  
  const comment = formatReviewComment(review);
  
  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/issues/${prNumber}/comments`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/vnd.github+json',
        'Content-Type': 'application/json',
        'X-GitHub-Api-Version': '2022-11-28'
      },
      body: JSON.stringify({
        body: comment
      })
    }
  );
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to post comment: ${error}`);
  }
  
  return response.json();
}

/**
 * Format review as markdown comment
 */
function formatReviewComment(review) {
  let comment = '## 🤖 Hermès AI Code Review\n\n';
  
  comment += `**Assessment:** ${review.assessment}\n\n`;
  
  if (review.issues.length > 0) {
    comment += '### ⚠️ Potential Issues\n';
    review.issues.forEach(issue => {
      comment += `- ${issue}\n`;
    });
    comment += '\n';
  }
  
  if (review.suggestions.length > 0) {
    comment += '### 💡 Suggestions\n';
    review.suggestions.forEach(suggestion => {
      comment += `- ${suggestion}\n`;
    });
    comment += '\n';
  }
  
  if (review.security.length > 0) {
    comment += '### 🔒 Security Concerns\n';
    review.security.forEach(sec => {
      comment += `- ${sec}\n`;
    });
    comment += '\n';
  }
  
  comment += '---\n';
  comment += '*🤖 Review generated by Hermès AI. Always verify critical suggestions.*\n';
  
  return comment;
}

/**
 * Handle pull request event
 */
async function handlePullRequest(event, payload) {
  const { action, pull_request: pr, repository } = payload;
  
  // Only review when PR is opened or updated
  if (!['opened', 'synchronize', 'reopened'].includes(action)) {
    console.log(`Skipping action: ${action}`);
    return;
  }
  
  console.log(`Reviewing PR #${pr.number}: ${pr.title}`);
  
  const owner = repository.owner.login;
  const repo = repository.name;
  const prNumber = pr.number;
  
  // Get PR diff and files
  const installationId = parseInt(process.env.INSTALLATION_ID || '0');
  const token = await getInstallationToken(installationId);
  
  // Get list of changed files
  const filesResponse = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/pulls/${prNumber}/files`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
      }
    }
  );
  
  if (!filesResponse.ok) {
    throw new Error(`Failed to get PR files: ${filesResponse.status}`);
  }
  
  const files = await filesResponse.json();
  
  const prData = {
    title: pr.title,
    body: pr.body,
    files: files.map(f => ({
      filename: f.filename,
      additions: f.additions,
      deletions: f.deletions,
      patch: f.patch
    }))
  };
  
  // Analyze with AI
  const review = await analyzeCodeChanges(prData, installationId);
  
  // Post comment
  await postReviewComment(owner, repo, prNumber, review);
  
  console.log(`Review posted for PR #${prNumber}`);
}

/**
 * Verify webhook signature
 */
function verifySignature(payload, signature) {
  if (!WEBHOOK_SECRET) return true; // Skip in development
  
  const crypto = require('crypto');
  const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET);
  const digest = 'sha256=' + hmac.update(payload).digest('hex');
  
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(digest));
}

/**
 * Main webhook handler
 */
async function handler(req, res) {
  // Only accept POST
  if (req.method !== 'POST') {
    return res.status(405).send('Method not allowed');
  }
  
  // Verify signature
  const signature = req.headers['x-hub-signature-256'];
  if (signature && !verifySignature(JSON.stringify(req.body), signature)) {
    return res.status(401).send('Invalid signature');
  }
  
  const event = req.headers['x-github-event'];
  const deliveryId = req.headers['x-github-delivery'];
  
  console.log(`Received event: ${event} (${deliveryId})`);
  
  try {
    const payload = req.body;
    
    switch (event) {
      case 'pull_request':
        await handlePullRequest(event, payload);
        break;
      case 'ping':
        console.log('Pong! App is connected.');
        break;
      default:
        console.log(`Unhandled event: ${event}`);
    }
    
    res.status(200).json({ ok: true });
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).json({ error: error.message });
  }
}

// Export for testing
module.exports = { handler, analyzeCodeChanges, formatReviewComment };

// Start server if run directly
if (require.main === module) {
  const express = require('express');
  const app = express();
  
  app.use(express.json());
  app.post('/webhook', handler);
  
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => {
    console.log(`Hermès Reviewer listening on port ${PORT}`);
  });
}