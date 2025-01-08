import React from 'react';
import { Box, Flex } from '@chakra-ui/react';
import { TypeAnimation } from 'react-type-animation';

const ChatComponent = ({ index, question }) => {
  return (
    <Flex w={'90%'} gap={'20px'} alignItems={'center'}>
      <Box ml={'20px'} fontSize={'20px'} whiteSpace="nowrap">
        질문 {index + 1}
      </Box>
      <Box w={'100%'} p={'13px 20px'} bg={'#ffffff'} borderRadius={'20px'}>
        <TypeAnimation
          sequence={[question, 2000]}
          speed={80}
          wrapper="span"
          cursor={false}
          repeat={0}
        />
      </Box>
    </Flex>
  );
};

export default ChatComponent;
