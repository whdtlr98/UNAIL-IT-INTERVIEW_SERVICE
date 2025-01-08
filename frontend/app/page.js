'use client';
import { Box, Flex, Image } from '@chakra-ui/react';
import { motion } from 'framer-motion';
import Header from './common/components/header';
import Container from './common/components/container';
import React from 'react';

const MotionBox = motion.create(Box);

export default function Home() {
  return (
    <Box w={'100%'} fontFamily={'inter'}>
      <Container>
        <Header />
        <Flex justify={'center'} alignItems={'center'} m={'0 80px'}>
          <Flex flex="1" justify={'center'}>
            <MotionBox
              initial={{ opacity: 0, y: 100 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.2 }}
              whileHover={{
                y: -10,
                transition: { duration: 1, delay: 0 },
              }}
              fontFamily={'inter'}
              textAlign={'center'}
              fontSize={{ xl: '34px', md: '30px' }}
              color={'#0066FF'}
            >
              <Image w={'500px'} src="/unail_main.png" />
            </MotionBox>
          </Flex>
          <Flex flex="1" justify={'center'}>
            <MotionBox
              initial={{ opacity: 0, y: 100 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.5 }}
              whileHover={{
                y: -10,
                transition: { duration: 1, delay: 0 },
              }}
              fontFamily={'inter'}
              textAlign={'center'}
              fontSize={{ xl: '34px', md: '30px' }}
              color={'#0066FF'}
            >
              <Box>AI 면접은 Unail,IT</Box>
              <Box>합격에 한걸음 더 다가가세요</Box>
            </MotionBox>
          </Flex>
        </Flex>
      </Container>
    </Box>
  );
}
