import { useCallback } from 'react';
import { deleteCookie, setCookie } from 'cookies-next';
import { useAtom } from 'jotai';
import { setBearerAuthorizationAtHttpClient } from '../common/utils/client';

import {
  accessTokenAtom,
  isUserLoadedAtom,
  refreshTokenAtom,
  userProfileAtom,
} from '../atom/useUserAtom';

export const refreshTokenCookieName = 'unailit_refresh-token';

export function useUserData() {
  const [accessToken, setAccessToken] = useAtom(accessTokenAtom);
  const [refreshToken, setRefreshToken] = useAtom(refreshTokenAtom);
  const [userProfileData, setUserProfileData] = useAtom(userProfileAtom);

  const userLogin = useCallback(
    ({ accessToken, refreshToken }) => {
      setAccessToken(accessToken);
      setRefreshToken(refreshToken);
      setCookie(refreshTokenCookieName, refreshToken, {
        maxAge: 60 * 60 * 24 * 1,
        sameSite: 'lax',
      });
      setBearerAuthorizationAtHttpClient(accessToken);
    },
    [setAccessToken, setRefreshToken]
  );

  const resetUser = useCallback(() => {
    setUserProfileData({
      userInfo: {
        name: '',
        email: '',
      },
    });
  }, [setUserProfileData]);

  const userLogout = useCallback(() => {
    setAccessToken('');
    setRefreshToken('');
    deleteCookie(refreshTokenCookieName);
    resetUser();
  }, [setAccessToken, setRefreshToken]);

  return {
    isLoggedIn:
      accessToken && refreshToken && accessToken !== '' && refreshToken !== '',
    accessToken,
    refreshToken,
    userLogin,
    userLogout,
    setUserProfileData,
    userProfileData,
  };
}
