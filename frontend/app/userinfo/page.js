import Header from '@/app/common/components/header';
import SideNavigation from '@/app/myPage/components/navigation';
import { Box, Flex } from '@chakra-ui/react';
import Container from '../common/components/container';
import UserComponent from './components/userComponent';
import React from 'react';
import UserGuard from '../common/utils/userGuard';

function UserInfo() {
  return (
    <UserGuard>
      <Container>
        <Header />
        <Flex mt={'50px'} gap={'30px'}>
          <SideNavigation />
          <Box w={'70%'}>
            <UserComponent />
          </Box>
        </Flex>
      </Container>
    </UserGuard>
  );
}

export default UserInfo;
