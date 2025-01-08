import React, { useEffect, useState } from 'react';
import { hasCookie, getCookie, deleteCookie } from 'cookies-next';
import { useUserData } from '@/app/api/useUserData';
import { accessTokenCookieName } from '@/app/oauth/callback/kakao/page';
import { useRouter, usePathname } from 'next/navigation';
import { useGetUserInfo } from '@/app/api/useGetUserInfo';
import { setRefreshTokenFailedCallback } from './client';

const refreshTokenCookieName = 'unailit_refresh-token';

export function UserProvider({ children }) {
  const router = useRouter();
  const [kakaoId, setKakaoId] = useState(null);

  const pathname = usePathname();

  const {
    userLogin,
    userLogout,
    accessToken,
    refreshToken,
    userProfileData,
    setUserProfileData,
  } = useUserData();

  useEffect(() => {
    const storedKakaoId = localStorage.getItem('id');
    if (storedKakaoId) {
      setKakaoId(storedKakaoId);
    }
  }, []);

  const { data: userInfo, isErorr: userInfoError } = useGetUserInfo(kakaoId);

  useEffect(() => {
    setRefreshTokenFailedCallback(() => {
      console.log('Redirecting to login page');
      if (pathname !== '/' || pathname !== '/about') {
        router.push('/login');
      }
    });
  }, [router]);

  useEffect(() => {
    if (hasCookie(refreshTokenCookieName)) {
      const refreshTokenFromCookie = getCookie(refreshTokenCookieName);
      const access_token = localStorage.getItem('access_token');

      if (refreshTokenFromCookie && access_token) {
        userLogin({
          accessToken: access_token,
          refreshToken: refreshTokenFromCookie,
        });
        if (userInfo) {
          setUserProfileData({
            userInfo: {
              name: userInfo.name,
              email: userInfo.email,
            },
          });
        }
      }
    }
  }, [userInfo, accessToken, refreshToken]);

  return <>{children}</>;
}
