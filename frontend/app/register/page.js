'use client';
import Header from '@/app/common/components/header';
import { Box, Flex } from '@chakra-ui/react';
import Container from '../common/components/container';
import React from 'react';
import RegisterInput from './components/registerInput';

function UserRegister() {
  return (
    <Container>
      <Header />
      <Box
        height="calc(100vh - 300px)"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <RegisterInput />
      </Box>
    </Container>
  );
}

export default UserRegister;
