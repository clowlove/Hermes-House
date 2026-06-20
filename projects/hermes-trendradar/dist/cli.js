#!/usr/bin/env node
"use strict";
/**
 * Hermès TrendRadar CLI
 * AI-powered trending topics aggregator
 */
const { Command } = require('commander');
const chalk = require('chalk');
const { getTrendingTopics, aggregateNews, analyzeSentiment } = require('./aggregator');
const program = new Command();
program
    .name('trendradar')
    .description('AI-powered trending topics aggregator')
    .version('1.0.0');
program
    .command('trending')
    .description('Get current trending topics')
    .option('-n, --num <number>', 'Number of topics', '10')
    .option('-p, --platforms <list>', 'Filter by platforms', '')
    .action(async (options) => {
    try {
        const topics = await getTrendingTopics({
            topN: parseInt(options.num || '10'),
            platforms: options.platforms ? options.platforms.split(',') : undefined
        });
        console.log(chalk.bold('\n📊 Trending Topics\n'));
        topics.forEach((topic, i) => {
            console.log(`${chalk.yellow((i + 1).toString())}. ${topic.keyword} (${topic.count})`);
        });
    }
    catch (error) {
        console.error(chalk.red('Error:'), error.message);
        process.exit(1);
    }
});
program
    .command('aggregate')
    .description('Aggregate news from multiple platforms')
    .option('-q, --query <text>', 'Filter by query')
    .option('-l, --limit <number>', 'Limit results', '50')
    .action(async (options) => {
    try {
        const news = await aggregateNews({
            query: options.query,
            limit: parseInt(options.limit || '50')
        });
        console.log(chalk.bold('\n📰 Aggregated News\n'));
        news.forEach((item, i) => {
            console.log(`${chalk.cyan((i + 1).toString())}. ${item.title}`);
            console.log(`   ${chalk.gray(item.platform)} • ${item.weight}\n`);
        });
    }
    catch (error) {
        console.error(chalk.red('Error:'), error.message);
        process.exit(1);
    }
});
program
    .command('sentiment')
    .description('Analyze sentiment of trending topics')
    .option('-t, --topic <text>', 'Topic to analyze', '')
    .action(async (options) => {
    try {
        const analysis = await analyzeSentiment(options.topic || '');
        console.log(chalk.bold('\n💭 Sentiment Analysis\n'));
        console.log(`Topic: ${chalk.yellow(options.topic || 'General')}`);
        console.log(`Positive: ${chalk.green(analysis.positive.toString())}%`);
        console.log(`Neutral: ${chalk.gray(analysis.neutral.toString())}%`);
        console.log(`Negative: ${chalk.red(analysis.negative.toString())}%`);
    }
    catch (error) {
        console.error(chalk.red('Error:'), error.message);
        process.exit(1);
    }
});
program.parse();
//# sourceMappingURL=cli.js.map