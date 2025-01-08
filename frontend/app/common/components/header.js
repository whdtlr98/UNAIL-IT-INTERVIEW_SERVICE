'use client';
import { Box, Image, Flex, Link } from '@chakra-ui/react';
import React, { useEffect } from 'react';
import { useUserData } from '@/app/api/useUserData';
import { useRouter } from 'next/navigation';

const Header = () => {
  const { isLoggedIn, userLogout } = useUserData();

  const router = useRouter();

  const onClickLogout = (event) => {
    event.preventDefault();
    userLogout();
    router.push('/login');
  };

  return (
    <Box
      display={'flex'}
      w={'100%'}
      p={'10px 30px'}
      color={'#0066FF'}
      justifyContent="space-between"
      fontSize={'28px'}
    >
      <Flex alignItems={'center'} gap={'40px'}>
        <Link href="/">
          <Box cursor={'pointer'}>
            <Image w={'80px'} mb={'5px'} src="/logo.png" />
          </Box>
        </Link>
        <Link href="/about">
          <Box w={'100%'}>About</Box>
        </Link>
        <Link href="/interview">
          <Box w={'100%'}>AI Mock Interview</Box>
        </Link>
        <Link href="/myPage">
          <Box w={'100%'}>My Page</Box>
        </Link>
      </Flex>

      <Flex alignItems={'center'} gap={'40px'}>
        {isLoggedIn ? (
          <Box w={'120px'} onClick={onClickLogout} cursor="pointer">
            Logout
          </Box>
        ) : (
          <Link href="/login">
            <Box w={'120px'}>Login</Box>
          </Link>
        )}
      </Flex>
    </Box>
  );
};

export default Header;
