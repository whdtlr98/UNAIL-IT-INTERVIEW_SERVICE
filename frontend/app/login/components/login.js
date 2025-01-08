'use client';
import { VStack, Text, Flex, Spacer, Link } from '@chakra-ui/react';
import KakaoLoginButton from './kakaoLoginButton';

const Login = () => {
  return (
    <Flex direction="column" minHeight="70vh">
      <Spacer />
      <VStack spacing={8} align="center" mb={10}>
        <Text fontSize="4xl" fontWeight="bold">
          로그인
        </Text>
        <Text fontSize="xl" color="#0066FF">
          당신을 더욱 빛나게 성장시킬 Unail,IT
        </Text>
        <KakaoLoginButton />
        <Text fontSize="sm" color="gray.500">
          로그인하여 다양한 기능을 이용해보세요
        </Text>
      </VStack>
      <Spacer />
      <Flex
        as="footer"
        justifyContent="center"
        p={5}
        borderTop="1px"
        borderColor="gray.200"
      >
        <Link href="/terms" mr={4} color="gray.500">
          이용약관
        </Link>
        <Link href="/privacy" color="gray.500">
          개인정보처리방침
        </Link>
      </Flex>
    </Flex>
  );
};

export default Login;
