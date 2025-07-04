// Arquivo: frontend/contexts/AuthContext.js
"use client"

import React, { createContext, useState, useContext, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const storedToken = localStorage.getItem('accessToken');
        if (storedToken) {
            setToken(storedToken);
        }
        setIsLoading(false);
    }, []);

    const login = (newToken) => {
        localStorage.setItem('accessToken', newToken);
        setToken(newToken);
        router.push('/');
    };

    const logout = () => {
        localStorage.removeItem('accessToken');
        setToken(null);
        router.push('/login');
    };
    
    // Adicionamos o 'user' ao contexto, mesmo que simples por enquanto
    const value = {
        token,
        user: token ? { name: 'admin' } : null, // Simplesmente para saber que há um usuário
        login,
        logout,
        isAuthenticated: !!token,
    };
    
    if (isLoading) {
        return <div className="flex h-screen items-center justify-center">Carregando aplicação...</div>;
    }

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};