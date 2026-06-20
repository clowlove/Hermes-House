/**
 * News Aggregator Module
 * Core functionality for aggregating and analyzing trending topics
 */
export interface TrendingTopic {
    keyword: string;
    count: number;
    platforms: string[];
    sentiment?: 'positive' | 'neutral' | 'negative';
}
export interface AggregatedNews {
    title: string;
    platform: string;
    url: string;
    weight: number;
    timestamp: Date;
    sentiment?: number;
}
export interface SentimentAnalysis {
    positive: number;
    neutral: number;
    negative: number;
    keywords: string[];
}
/**
 * Get trending topics from aggregated sources
 */
export declare function getTrendingTopics(options: {
    topN?: number;
    platforms?: string[];
    extractMode?: 'keywords' | 'auto_extract';
}): Promise<TrendingTopic[]>;
/**
 * Aggregate news from multiple platforms
 */
export declare function aggregateNews(options: {
    query?: string;
    limit?: number;
}): Promise<AggregatedNews[]>;
/**
 * Analyze sentiment of a topic
 */
export declare function analyzeSentiment(topic: string): Promise<SentimentAnalysis>;
//# sourceMappingURL=aggregator.d.ts.map