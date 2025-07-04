// Arquivo: frontend/lib/api.js

const apiBaseUrl = "http://192.168.1.9:8000";

// Função auxiliar que monta a requisição com o token
const fetchWithAuth = async (path, options = {}) => {
    const token = localStorage.getItem('accessToken');

    const headers = {
        'Accept': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Se o body for FormData, não definimos Content-Type. O navegador faz isso.
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${apiBaseUrl}${path}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        // Se o token for inválido ou expirado, limpa e redireciona para o login
        localStorage.removeItem('accessToken');
        window.location.href = '/login';
        throw new Error("Sessão expirada. Por favor, faça o login novamente.");
    }
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Erro desconhecido" }));
        throw new Error(errorData.detail || "Ocorreu um erro na requisição.");
    }

    return response;
};

// Funções específicas para cada tipo de método HTTP
export const apiGet = (path) => fetchWithAuth(path, { method: 'GET' });
export const apiPost = (path, body) => fetchWithAuth(path, { method: 'POST', body: JSON.stringify(body) });
export const apiPut = (path, body) => fetchWithAuth(path, { method: 'PUT', body: JSON.stringify(body) });
export const apiDelete = (path) => fetchWithAuth(path, { method: 'DELETE' });