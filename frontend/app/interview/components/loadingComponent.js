import React, { useState, useEffect } from 'react';
import { Flex, Spinner, Fade, Text } from '@chakra-ui/react';


const LoadingComponent = () => {
  const [textIndex, setTextIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(true);
  const texts = ['면접을 준비중입니다', '잠시만 기다려주세요'];

  useEffect(() => {
    const interval = setInterval(() => {
      setIsVisible(false);
      setTimeout(() => {
        setTextIndex((prevIndex) => (prevIndex + 1) % texts.length);
        setIsVisible(true);
      }, 500); // 페이드 아웃 후 0.5초 뒤에 다음 텍스트로 변경
    }, 3000); // 3초마다 텍스트 변경

    return () => clearInterval(interval);
  }, []);

  return (
    <Flex
      width="100vw"
      height="50vh"
      justifyContent="center"
      alignItems="center"
      flexDirection="column"
    >
      <Spinner
        thickness="4px"
        speed="0.65s"
        emptyColor="gray.200"
        color="blue.500"
        size="xl"
        mb={4}
      />
      <Fade in={isVisible}  transition={{ enter: { duration: 0.5 }, exit: { duration: 0.5 } }}>
        <Text fontSize={'xl'}>
        {texts[textIndex]}
        </Text>
      </Fade>
    </Flex>
  );
};


  export default LoadingComponent;