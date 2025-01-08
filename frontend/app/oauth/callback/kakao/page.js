'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { useUserData } from '@/app/api/useUserData';
import { Center, Spinner, VStack } from '@chakra-ui/react';

export const accessTokenCookieName = 'unailit_access-token';

const KakaoCallbackPage = () => {
  const { userLogin } = useUserData();
  const [code, setCode] = useState(null);
  const router = useRouter();

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URL(window.location.href).searchParams;
      const codeParam = urlParams.get('code');
      if (codeParam) {
        setCode(codeParam);
      }
    }
  }, []);

  useEffect(() => {
    if (code !== null) {
      kakaoLogin();
    }
  }, [code]);

  const kakaoLogin = async () => {
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/login/oauth/code/kakao?code=${code}`,
        // `https://api.aiunailit.com/login/oauth/code/kakao?code=${code}`,
        { withCredentials: true }
      );
      if (res.status === 200) {
        if (res.data.message === '회원가입 필요') {
          router.replace('/register');
        } else if (res.data.message === '로그인 성공') {
          const { access_token, refresh_token, id } = res.data.user;
          localStorage.setItem('id', id);

          localStorage.setItem('access_token', access_token);

          userLogin({
            accessToken: access_token,
            refreshToken: refresh_token,
          });

          router.replace('/');
        }
      }
    } catch (error) {
      console.error('Login failed:', error);
      if (error.response) {
        console.error('Error response:', error.response.data);
      }
      router.replace('/login');
    }
  };

  return (
    <Center height="100vh">
      <VStack spacing={4}>
        <Spinner size="xl" color="blue.500" thickness="4px" />
      </VStack>
    </Center>
  );
};

export default KakaoCallbackPage;
