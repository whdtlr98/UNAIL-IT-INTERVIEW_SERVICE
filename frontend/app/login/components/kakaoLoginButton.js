'use client';
import { Box, Link, Image } from '@chakra-ui/react';
import React from 'react';

const KakaoLoginButton = () => {
  const KAKAO_AUTH_URL = `https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=d1561b312e7d598361f42f47d8baf198&redirect_uri=http://localhost:3000/oauth/callback/kakao&scope=profile_nickname`;
  // const KAKAO_AUTH_URL = `https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=${KAKAO_REST_API_KEY}&redirect_uri=${KAKAO_REDIRECT_URI}&scope=profile_nickname`;

  return (
    <Link href={KAKAO_AUTH_URL} _hover={{ opacity: 0.8 }}>
      <Box
        as="button"
        display="flex"
        alignItems="center"
        justifyContent="center"
        bg="transparent"
        border="none"
        w={'300px'}
      >
        <Image src="/kakao_login.png" alt="카카오 로그인" />
      </Box>
    </Link>
  );
};

export default KakaoLoginButton;
