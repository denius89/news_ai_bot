import React, { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const AuthDebugger: React.FC = () => {
    const { authHeaders, setAuthHeaders, user, isAuthenticated, loading, error } = useAuth();

    useEffect(() => {
        // Принудительно устанавливаем правильные заголовки для разработки
        if (!isAuthenticated && !loading && !error) {
            console.log('🔧 AuthDebugger: Setting fake auth headers');
            
            const fakeHeaders = {
                'X-Telegram-Init-Data': '',
                'X-Telegram-User-Data': 'eyJpZCI6OTk5OTk5OTk5LCJmaXJzdF9uYW1lIjoiRGV2IEFkbWluIiwidXNlcm5hbWUiOiJkZXZfYWRtaW4ifQ=='
            };
            
            // Используем setTimeout чтобы избежать конфликта с AuthContext
            setTimeout(() => {
                setAuthHeaders(fakeHeaders);
                console.log('🔧 AuthDebugger: Headers set:', fakeHeaders);
            }, 100);
        }
    }, [isAuthenticated, loading, error, setAuthHeaders]);

    // Отладочная информация
    if (process.env.NODE_ENV === 'development') {
        return (
            <div 
                style={{ 
                    position: 'fixed', 
                    top: 0, 
                    left: 0, 
                    background: 'black', 
                    color: 'white', 
                    padding: '10px', 
                    fontSize: '12px',
                    zIndex: 9999,
                    maxWidth: '300px',
                    border: '2px solid red'
                }}
            >
                <div><strong>AuthDebugger:</strong></div>
                <div>Auth Headers: {JSON.stringify(authHeaders)}</div>
                <div>Is Authenticated: {isAuthenticated ? 'Yes' : 'No'}</div>
                <div>User ID: {user?.user_id || 'None'}</div>
                <div>Loading: {loading ? 'Yes' : 'No'}</div>
                <div>Error: {error || 'None'}</div>
                <div>Headers Length: {Object.keys(authHeaders).length}</div>
            </div>
        );
    }

    return null;
};

export default AuthDebugger;
