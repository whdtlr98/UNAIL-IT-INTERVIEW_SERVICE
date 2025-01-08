import Container from '@/app/common/components/container';
import Header from '@/app/common/components/header';
import SideNavigation from '@/app/myPage/components/navigation';
import { Box, Flex } from '@chakra-ui/react';
import CreateBoard from '../components/createBoard';
import React from 'react';
import UserGuard from '@/app/common/utils/userGuard';

const BoardCreate = () => {
  return (
    <UserGuard>
      <Container>
        <Header />
        <Flex w={'90%'} justifyContent={'space-between'}>
          <SideNavigation />
          <Box w={'70%'}>
            <CreateBoard />
          </Box>
        </Flex>
      </Container>
    </UserGuard>
  );
};

export default BoardCreate;
