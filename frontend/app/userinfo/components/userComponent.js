'use client';
import {
  Box,
  Button,
  Input,
  InputGroup,
  InputRightElement,
  Text,
  useDisclosure,
} from '@chakra-ui/react';
import React from 'react';

import { useState } from 'react';
import WithDrawModal from './withdraw';
import { useUserData } from '@/app/api/useUserData';

const UserComponent = () => {
  const [onWithDraw, setOnWithDraw] = useState(false);
  const { userProfileData } = useUserData();

  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <Box>
      <Box maxWidth="800px" margin="auto" p={5} overflowX={'scroll'}>
        <Box borderBottom={'4px solid black'} pb={'10px'} w={'100%'}>
          <Text fontSize={['24px', '26px', '30px']}>회원 정보</Text>
        </Box>
        <Box p={'20px 0 20px 0'}>
          <Box fontSize={'20px'} mb={1}>
            이름
          </Box>
          <Box borderRadius={'15px'} p={'5px 10px'} w={'100%'} bg={'white'}>
            {userProfileData.userInfo.name}
          </Box>
        </Box>
        <Box p={'20px 0 20px 0'}>
          <Box fontSize={'20px'} mb={1}>
            이메일
          </Box>
          <InputGroup>
            <Input type="file" accept=".pdf" display="none" />
            <Input
              w={'100%'}
              h={'40px'}
              placeholder="test@naver.com"
              border={'0'}
              borderRadius={'15px'}
              background={'white'}
              value={userProfileData.userInfo.email}
              readOnly
              sx={{
                '::placeholder': {
                  color: 'gray.500',
                },
              }}
            />
            <InputRightElement width="80px" height="100%">
              <Button
                // onClick={() =>
                //   document.querySelector('input[type="file"]').click()
                // }
                variant="ghost"
                aria-label="Upload file"
                fontSize="28px"
                paddingRight="10px"
              >
                <Box fontSize={'md'} color={'gray.500'}>
                  수정하기
                </Box>
              </Button>
            </InputRightElement>
          </InputGroup>
        </Box>
        <Box p={'20px 0 20px 0'}>
          <Box fontSize={'20px'} mb={1}>
            회원탈퇴
          </Box>
          <Button
            fontSize={'md'}
            color={'red'}
            borderRadius={'15px'}
            p={'5px 20px'}
            bg={'white'}
            onClick={onOpen}
          >
            회원탈퇴
          </Button>
        </Box>
      </Box>
      <WithDrawModal isOpen={isOpen} onClose={onClose} />
    </Box>
  );
};

export default UserComponent;
