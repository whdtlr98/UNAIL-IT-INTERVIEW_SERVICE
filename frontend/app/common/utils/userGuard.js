'use client';

import { useEffect, useState } from 'react';
import { useCookies } from 'react-cookie';
import { hasCookie, getCookie, deleteCookie } from 'cookies-next';
import { useRouter, usePathname } from 'next/navigation';
import { Spinner, Flex } from '@chakra-ui/react';
import { refreshTokenCookieName } from '@/app/api/useUserData';
import { accessTokenCookieName } from '@/app/oauth/callback/kakao/page';

const UserGuard = ({ children }) => {
  const accessToken = getCookie(accessTokenCookieName);
  const router = useRouter();
  const pathname = usePathname();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');

    const unprotectedRoutes = ['/', '/about', '/login'];

    if (!accessToken && !unprotectedRoutes.includes(pathname)) {
      router.push('/login');
    } else {
      setIsLoading(false);
    }
  }, [accessToken, router, pathname]);

  if (pathname === '/' || pathname === '/about') {
    return <>{children}</>;
  }

  if (isLoading && pathname !== '/login') {
    return (
      <Flex
        width="100vw"
        height="100vh"
        justifyContent="center"
        alignItems="center"
      >
        <Spinner
          thickness="4px"
          speed="0.65s"
          emptyColor="gray.200"
          color="blue.500"
          size="xl"
        />
      </Flex>
    );
  }

  return <>{children}</>;
};

export default UserGuard;
