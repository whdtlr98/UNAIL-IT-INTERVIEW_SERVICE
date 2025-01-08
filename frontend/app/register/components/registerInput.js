'use client';

import {
  Box,
  Flex,
  Spacer,
  VStack,
  Text,
  Input,
  Button,
} from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useRegister } from '@/app/api/useRegister';

const RegisterInput = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const {
    mutate: register,
    isError: registerError,
    data: isRegister,
  } = useRegister();

  const onChangeNmae = (e) => {
    setName(e.target.value);
  };

  const onChangeEmail = (e) => {
    setEmail(e.target.value);
  };

  const onRegister = (e) => {
    e.preventDefault();
    const currentDate = new Date().toISOString().split('T')[0];
    const kakaoId = 'id';

    const data = {
      name: name,
      email: email,
      id: kakaoId,
      user_joined: currentDate,
    };

    register(data);
  };

  return (
    <Flex direction="column" minHeight="100vh">
      <Spacer />
      <VStack spacing={8} align="center" mb={10}>
        <Text fontSize="4xl" fontWeight="bold">
          회원가입
        </Text>
        <Text fontSize="xl" color="#0066FF">
          당신을 더욱 빛나게 성장시킬 Unail,IT
        </Text>
        <Input
          value={name}
          onChange={(e) => onChangeNmae(e)}
          bg={'#fff'}
          placeholder="이름"
          type="text"
        />
        <Input
          value={email}
          onChange={(e) => onChangeEmail(e)}
          bg={'#fff'}
          placeholder="이메일"
          type="email"
        />
        <Button
          w={'100%'}
          color={'#fff'}
          background={'#0066FF'}
          fontFamily={'inter'}
          onClick={onRegister}
        >
          가입 하기
        </Button>
      </VStack>
      <Spacer />
    </Flex>
  );
};

export default RegisterInput;
