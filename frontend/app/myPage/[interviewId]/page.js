'use client';
import Container from '@/app/common/components/container';
import Header from '@/app/common/components/header';
import { Box, Flex } from '@chakra-ui/react';
import SideNavigation from '../components/navigation';
import DetailLog from '../components/detailLog';
import React from 'react';
import UserGuard from '@/app/common/utils/userGuard';
import { GetInterviewLog } from '../hook/useGetInterviewLog';
import { GetInterviewReport } from '../hook/useGetInterviewReport';

const InterviewDetail = ({ params }) => {
  const { interviewLogList } = GetInterviewLog(params.interviewId);

  const { reportData } = GetInterviewReport(params.interviewId);

  return (
    <UserGuard>
      <Container>
        <Header />
        <Flex mt={'50px'} gap={'30px'}>
          <SideNavigation />
          <Box w={'70%'}>
            <DetailLog interviewLogList={interviewLogList} reportData={reportData} />
          </Box>
        </Flex>
      </Container>
    </UserGuard>
  );
};

export default InterviewDetail;
