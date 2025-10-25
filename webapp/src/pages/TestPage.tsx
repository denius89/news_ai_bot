import React, { useEffect, useState } from 'react';

const TestPage: React.FC = () => {
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Тестируем различные API endpoints
        const testEndpoints = [
            '/api/news/latest',
            '/api/digests/categories',
            '/api/events/categories',
            '/api/analytics/digest-stats'
        ];

        const testEndpoint = async (endpoint: string) => {
            try {
                console.log(`Testing ${endpoint}...`);
                const response = await fetch(endpoint);
                const data = await response.json();
                console.log(`${endpoint} response:`, data);

                // Тестируем Object.values на каждом поле
                if (data && typeof data === 'object') {
                    Object.keys(data).forEach(key => {
                        const value = data[key];
                        console.log(`Testing Object.values on data.${key}:`, value);

                        if (value && typeof value === 'object') {
                            try {
                                const values = Object.values(value);
                                console.log(`✅ Object.values(data.${key}) success:`, values);
                            } catch (err) {
                                console.error(`❌ Object.values(data.${key}) failed:`, err);
                                setError(`Object.values failed on ${endpoint}.${key}: ${err}`);
                            }
                        }
                    });
                }
            } catch (err) {
                console.error(`❌ ${endpoint} failed:`, err);
                setError(`${endpoint} failed: ${err}`);
            }
        };

        // Тестируем все endpoints
        testEndpoints.forEach(endpoint => testEndpoint(endpoint));
    }, []);

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
            <h1 className="text-2xl font-bold mb-4">API Test Page</h1>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    <strong>Error:</strong> {error}
                </div>
            )}

            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg">
                <h2 className="text-lg font-semibold mb-2">Test Results</h2>
                <p>Check browser console for detailed test results.</p>
                <p>This page tests all API endpoints for Object.values compatibility.</p>
            </div>
        </div>
    );
};

export default TestPage;
