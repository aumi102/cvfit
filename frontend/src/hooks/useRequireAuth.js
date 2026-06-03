'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { me } from '@/services/authApi';
import { clearAuthSession, getStoredAuthToken, storeSafeUser } from '@/services/authStorage';

export function useRequireAuth() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [isAuthChecking, setIsAuthChecking] = useState(true);

  useEffect(() => {
    let active = true;
    const token = getStoredAuthToken();
    if (!token) {
      clearAuthSession();
      router.push('/login');
      return;
    }

    (async () => {
      try {
        const currentUser = await me();
        if (!active) return;
        setUser(storeSafeUser(currentUser));
        setIsAuthChecking(false);
      } catch {
        if (!active) return;
        clearAuthSession();
        router.push('/login');
      }
    })();

    return () => {
      active = false;
    };
  }, [router]);

  return { user, isAuthChecking };
}
