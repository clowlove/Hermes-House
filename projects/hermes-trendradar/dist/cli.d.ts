#!/usr/bin/env node
/**
 * Hermès TrendRadar CLI
 * AI-powered trending topics aggregator
 */
declare const Command: any;
declare const chalk: any;
declare const getTrendingTopics: any, aggregateNews: any, analyzeSentiment: any;
declare const program: any;
interface TrendingOptions {
    num?: string;
    platforms?: string;
}
interface AggregateOptions {
    query?: string;
    limit?: string;
}
interface SentimentOptions {
    topic?: string;
}
interface Topic {
    keyword: string;
    count: number;
}
interface NewsItem {
    title: string;
    platform: string;
    weight: number;
}
//# sourceMappingURL=cli.d.ts.map