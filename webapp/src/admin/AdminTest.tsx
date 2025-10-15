/**
 * Простой тест компонент для проверки админ панели
 */

export function AdminTest() {
  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0' }}>
      <h1 style={{ color: '#22c55e' }}>🔧 Admin Panel Test</h1>
      <p>Если вы видите этот текст, админ панель работает!</p>
      <div style={{ marginTop: '20px' }}>
        <button 
          onClick={() => alert('Admin Panel работает!')}
          style={{
            padding: '10px 20px',
            backgroundColor: '#22c55e',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Тест кнопки
        </button>
      </div>
    </div>
  );
}

