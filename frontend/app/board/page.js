import Container from '@/app/common/components/container';
import Header from '../common/components/header';
import SideNavigation from '../myPage/components/navigation';
import BoardList from './components/boardList';
import { Flex } from '@chakra-ui/react';
import React from 'react';
import UserGuard from '../common/utils/userGuard';

function Board() {
  return (
    <UserGuard>
      <Container>
        <Header />
        <Flex w={'90%'} justifyContent={'center'}>
          <SideNavigation />
          <BoardList />
        </Flex>
      </Container>
    </UserGuard>
  );
}

export default Board;
