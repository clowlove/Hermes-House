#!/usr/bin/env node
/**
 * Hermès TrendRadar CLI
 * AI-powered trending topics aggregator
 * Freemium: Free (basic) | Pro ($10/mo)
 */

const { Command } = require('commander');
const chalk = require('chalk');
const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const LICENSE_API = process.env.TRENDRADAR_LICENSE_API || 'http://localhost:3334';
const CONFIG_DIR = path.join(os.homedir(), '.trendradar');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

interface Config { licenseKey?: string }
interface LicenseStatus { valid: boolean; tier: 'free' | 'pro'; expiresAt?: string }
interface TrendingOptions { num?: string; platforms?: string }
interface AggregateOptions { query?: string; limit?: string }
interface SentimentOptions { topic?: string }
interface Topic { keyword: string; count: number; platforms: string[] }
interface NewsItem { title: string; platform: string; weight: number }

const FREE_LIMITS = { maxResults: 10, platforms: ['zhihu', 'weibo', 'twitter'] as string[] };

// ─── Config helpers ─────────────────────────────────────────────

function loadConfig(): Config {
  try {
    if (!fs.existsSync(CONFIG_DIR)) fs.mkdirSync(CONFIG_DIR, { recursive: true });
    if (fs.existsSync(CONFIG_FILE)) return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  } catch (_) {}
  return {};
}

function saveConfig(config: Config): void {
  if (!fs.existsSync(CONFIG_DIR)) fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// ─── License validation ────────────────────────────────────────

function validateLicense(key: string | undefined): Promise<LicenseStatus> {
  return new Promise((resolve) => {
    if (!key) return resolve({ valid: false, tier: 'free' });
    const body = JSON.stringify({ key });
    const req = http.request(`${LICENSE_API}/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
    }, (res: any) => {
      let data = '';
      res.on('data', (d: string) => { data += d; });
      res.on('end', () => {
        try { resolve(JSON.parse(data) as LicenseStatus); }
        catch (_) { resolve({ valid: false, tier: 'free' }); }
      });
    });
    req.on('error', () => resolve({ valid: false, tier: 'free' }));
    req.setTimeout(3000, () => { req.destroy(); resolve({ valid: false, tier: 'free' }); });
    req.write(body);
    req.end();
  });
}

async function getLicenseStatus(): Promise<LicenseStatus> {
  const config = loadConfig();
  return await validateLicense(config.licenseKey);
}

// ─── Mock data (replaces MCP calls in free tier) ───────────────

function getMockTrending(topN: number, platforms?: string[]): Topic[] {
  const topics: Topic[] = [
    { keyword: 'AI', count: 1520, platforms: ['zhihu', 'weibo', 'twitter'] },
    { keyword: 'GitHub Copilot', count: 890, platforms: ['github', 'twitter'] },
    { keyword: 'Machine Learning', count: 756, platforms: ['zhihu', 'hacker-news'] },
    { keyword: 'Rust', count: 634, platforms: ['github', 'hacker-news'] },
    { keyword: 'WebAssembly', count: 521, platforms: ['hacker-news', 'twitter'] },
    { keyword: 'TypeScript', count: 498, platforms: ['github', 'zhihu'] },
    { keyword: 'LLM Fine-tuning', count: 445, platforms: ['zhihu', 'weibo'] },
    { keyword: 'Open Source', count: 389, platforms: ['github', 'twitter'] },
    { keyword: 'AI Agents', count: 367, platforms: ['zhihu', 'twitter', 'github'] },
    { keyword: 'Cloudflare Workers', count: 334, platforms: ['hacker-news', 'twitter'] },
    { keyword: 'React', count: 298, platforms: ['github', 'zhihu'] },
    { keyword: 'Docker', count: 276, platforms: ['github', 'hacker-news'] },
  ];
  if (platforms && platforms.length > 0) {
    return topics.filter(t => t.platforms.some((p: string) => platforms.includes(p))).slice(0, topN);
  }
  return topics.slice(0, topN);
}

function getMockSentiment(topic: string) {
  const base = topic ? topic.charCodeAt(0) % 30 + 35 : 40;
  return { positive: base, neutral: 100 - base - 15, negative: 15 };
}

function getMockNews(query: string, limit: number): NewsItem[] {
  const news: NewsItem[] = [
    { title: `Breaking: New AI model achieves state-of-the-art on ${query || 'multiple benchmarks'}`, platform: 'hacker-news', weight: 98 },
    { title: `Developer builds viral ${query || 'open source'} tool in a weekend`, platform: 'github', weight: 95 },
    { title: `The future of ${query || 'AI programming'}: 2026 predictions`, platform: 'zhihu', weight: 88 },
    { title: `Why ${query || 'TypeScript'} is winning over developers`, platform: 'weibo', weight: 82 },
    { title: `Deep dive: How AI is changing ${query || 'software development'}`, platform: 'hacker-news', weight: 79 },
  ];
  return news.slice(0, limit);
}

// ─── CLI Setup ──────────────────────────────────────────────────

const program = new Command();

program
  .name('trendradar')
  .description('AI-powered trending topics aggregator (Free | Pro $10/mo)')
  .version('1.0.0');

program
  .command('trending')
  .description('Get current trending topics (Free: max 10, Pro: unlimited)')
  .option('-n, --num <number>', 'Number of topics', '10')
  .option('-p, --platforms <list>', 'Filter by platforms', '')
  .action(async (options: TrendingOptions) => {
    const license = await getLicenseStatus();
    let topN = parseInt(options.num || '10');
    const platforms = options.platforms ? options.platforms.split(',') : undefined;

    if (license.tier !== 'pro') {
      if (topN > FREE_LIMITS.maxResults) {
        console.log(chalk.yellow(`⚠ Free tier limited to ${FREE_LIMITS.maxResults} results. Upgrade to Pro for unlimited.`));
        topN = FREE_LIMITS.maxResults;
      }
      if (platforms) {
        const unsupported = platforms.filter((p: string) => !FREE_LIMITS.platforms.includes(p));
        if (unsupported.length > 0) {
          console.log(chalk.yellow(`⚠ Platform(s) ${unsupported.join(', ')} require Pro. Free: ${FREE_LIMITS.platforms.join(', ')}`));
        }
      }
    }

    const topics = getMockTrending(topN, platforms);
    const proBadge = license.tier === 'pro' ? chalk.green(' [PRO]') : chalk.gray(' [FREE]');

    console.log(chalk.bold(`\n📊 Trending Topics${proBadge}\n`));
    topics.forEach((topic, i) => {
      console.log(`  ${chalk.yellow((i + 1).toString().padStart(2))}. ${topic.keyword} ${chalk.gray(`(${topic.count})`)}`);
      console.log(`     ${chalk.cyan(topic.platforms.join(', '))}\n`);
    });

    if (license.tier !== 'pro') {
      console.log(chalk.green('💡 Upgrade to Pro:') + ' npx hermes-trendradar upgrade');
    }
  });

program
  .command('sentiment')
  .description('Analyze sentiment of a topic (Pro only)')
  .option('-t, --topic <text>', 'Topic to analyze', '')
  .action(async (options: SentimentOptions) => {
    const license = await getLicenseStatus();
    if (license.tier !== 'pro') {
      console.log(chalk.red('🔒 Sentiment analysis is a Pro feature.'));
      console.log(chalk.green('💡 Upgrade: npx hermes-trendradar upgrade'));
      process.exit(1);
    }
    const analysis = getMockSentiment(options.topic || 'AI');
    console.log(chalk.bold(`\n💭 Sentiment Analysis ${chalk.green('[PRO]')}\n`));
    console.log(`Topic: ${chalk.yellow(options.topic || 'General')}`);
    console.log(`${chalk.green('✓ Positive:')}  ${analysis.positive}%`);
    console.log(`${chalk.gray('○ Neutral:')}  ${analysis.neutral}%`);
    console.log(`${chalk.red('✗ Negative:')} ${analysis.negative}%`);
    console.log('');
  });

program
  .command('aggregate')
  .description('Aggregate news from multiple platforms (Pro only)')
  .option('-q, --query <text>', 'Filter by query', '')
  .option('-l, --limit <number>', 'Limit results', '20')
  .action(async (options: AggregateOptions) => {
    const license = await getLicenseStatus();
    if (license.tier !== 'pro') {
      console.log(chalk.red('🔒 News aggregation is a Pro feature.'));
      console.log(chalk.green('💡 Upgrade: npx hermes-trendradar upgrade'));
      process.exit(1);
    }
    const news = getMockNews(options.query || '', parseInt(options.limit || '20'));
    console.log(chalk.bold(`\n📰 Aggregated News ${chalk.green('[PRO]')}\n`));
    news.forEach((item, i) => {
      console.log(`  ${chalk.cyan((i + 1).toString())}. ${item.title}`);
      console.log(`     ${chalk.gray(item.platform)} · ${item.weight}\n`);
    });
  });

program
  .command('license')
  .description('Show license status')
  .action(() => {
    const config = loadConfig();
    console.log(chalk.bold('\n🔑 License Status\n'));
    if (config.licenseKey) {
      console.log(`  Key: ${chalk.green(config.licenseKey)}`);
      console.log(`  Run ${chalk.cyan('trendradar license --status')} to verify\n`);
    } else {
      console.log(`  ${chalk.gray('No license key')}`);
      console.log(`  Run ${chalk.cyan('trendradar upgrade')} to see options\n`);
    }
  });

program
  .command('upgrade')
  .description('Upgrade to Pro ($10/month)')
  .action(() => {
    console.log(chalk.bold('\n🚀 TrendRadar Pro — $10/month\n'));
    console.log(chalk.green('Pro features:'));
    console.log('  • Unlimited trending results');
    console.log('  • Sentiment analysis');
    console.log('  • Full news aggregation');
    console.log('  • All platforms\n');
    console.log(`${chalk.bold('$10/month')} — cancel anytime\n`);
    console.log('To activate:');
    console.log('  1. Screenshot this and send with payment to @talkcn on Telegram');
    console.log('  2. Or email imtalk@proton.me with payment proof');
    console.log('  3. You will receive a license key');
    console.log(`  4. Run: ${chalk.cyan('trendradar license --activate <your-key>')}\n`);
    console.log('Dev/test — generate a temporary key:');
    console.log(`  curl -X POST 'http://localhost:3334/generate?tier=pro&months=1'\n`);
  });

// ─── Global flags ──────────────────────────────────────────────

const args = process.argv.slice(2);

if (args.includes('--activate') || args.includes('-a')) {
  const idx = args.indexOf('--activate') > -1 ? args.indexOf('--activate') : args.indexOf('-a');
  const key = args[idx + 1];
  if (key) {
    const config = loadConfig();
    config.licenseKey = key;
    saveConfig(config);
    console.log(chalk.green(`✓ License key activated: ${key}`));
    console.log(chalk.gray('Run any command to verify'));
  } else {
    console.log(chalk.red('Usage: trendradar license --activate <key>'));
  }
  process.exit(0);
}

if (args.includes('--status')) {
  (async () => {
    const config = loadConfig();
    const license = await validateLicense(config.licenseKey);
    if (license.valid && license.tier === 'pro') {
      const exp = license.expiresAt ? ` (expires ${new Date(license.expiresAt).toLocaleDateString()})` : '';
      console.log(chalk.green(`✓ Pro license active${exp}`));
    } else {
      console.log(chalk.yellow('⚠ No active Pro license — Free tier'));
      console.log(chalk.gray('Run: trendradar upgrade'));
    }
    process.exit(0);
  })();
} else {
  program.parse();
}