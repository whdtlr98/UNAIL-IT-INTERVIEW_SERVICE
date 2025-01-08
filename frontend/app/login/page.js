import { Box } from '@chakra-ui/react';
import Container from '../common/components/container';
import Header from '../common/components/header';
import Login from './components/login';
import React from 'react';

async function LoginPage() {
  return (
    <Container>
      <Header />
      <Box
        height="calc(100vh - 300px)"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Login />
      </Box>
    </Container>
  );
}

export default LoginPage;
