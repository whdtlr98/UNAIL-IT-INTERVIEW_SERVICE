'use client';
import { useGetInterviewHistory } from '@/app/api/useGetInterviewHistory';
import { Box, Text, VStack, Grid, GridItem, Link } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { formatDate } from '@/app/common/utils/dayformat';
import { useGetUserInfo } from '@/app/api/useGetUserInfo';
import { useUserData } from '@/app/api/useUserData';
import { getCookie } from 'cookies-next';
import { refreshTokenCookieName } from '@/app/api/useUserData';
import { accessTokenCookieName } from '@/app/oauth/callback/kakao/page';

const InterviewLog = ({ date, id }) => {
  return (
    <Box
      display={'grid'}
      p={'20px'}
      fontSize={'20px'}
      bg={'white'}
      w={'300px'}
      borderRadius={'16px'}
      cursor={'pointer'}
      transition="transform 0.2s ease-in-out"
      _hover={{ transform: 'translateY(-5px)' }}
    >
      <Link href={`/myPage/${id}`}>
        <Text>{id}번째 면접</Text>
        <Text>{formatDate(date)}</Text>
      </Link>
    </Box>
  );
};

const InterviewHistory = () => {
  const [kakaoId, setKakaoId] = useState(null);
  const { userLogin, setUserProfileData } = useUserData();

  useEffect(() => {
    const storedKakaoId = localStorage.getItem('id');
    if (storedKakaoId) {
      setKakaoId(storedKakaoId);
    }
  }, []);

  useEffect(() => {
    const refreshTokenFromCookie = getCookie(refreshTokenCookieName);
    const accessTokenFromCookie = getCookie(accessTokenCookieName);

    if (refreshTokenFromCookie && accessTokenFromCookie) {
      userLogin({
        accessToken: accessTokenFromCookie,
        refreshToken: refreshTokenFromCookie,
      });
    }
  }, []);

  const { data: interviewHistoryData, isError: interviewHistoryError } =
    useGetInterviewHistory(kakaoId);

  const { data: userInfo, isErorr: userInfoError } = useGetUserInfo(kakaoId);

  const [interviewData, setInterviewData] = useState([]);

  useEffect(() => {
    if (interviewHistoryData) {
      setInterviewData(interviewHistoryData);
    }
  }, [interviewHistoryData]);

  return (
    <Box>
      <Box borderBottom={'4px solid black'} pb={'10px'} w={'100%'}>
        <Text fontSize={['24px', '26px', '30px']}>면접 이력</Text>
      </Box>
      <Grid w={'100%'} pt={'30px'} templateColumns="repeat(3, 1fr)" gap={6} pb={'50px'}>
        {interviewData.map((interview) => (
          <GridItem key={interview.interview_id}>
            <InterviewLog
              date={interview.interview_created}
              id={interview.interview_id}
            />
          </GridItem>
        ))}
      </Grid>
    </Box>
  );
};

export default InterviewHistory;
