'use client';
import { useGetBoardDetailQuery } from '@/app/api/useBoardClient';
import { formatDate } from '@/app/common/utils/dayformat';
import { Box, Flex, Text, Textarea } from '@chakra-ui/react';
import { useParams } from 'next/navigation';
import { useEffect } from 'react';

const DetailComponent = () => {
  const params = useParams();
  const boardId = params.id;

  const { data: BoardDetail, error: isErrorBoardDetail } =
    useGetBoardDetailQuery(boardId);

  return (
    <Box p={5} w={'100%'}>
      <Flex justifyContent="space-between" alignItems="center" mb={5}>
        <Flex
          fontSize={'xl'}
          borderBottom={'4px solid black'}
          pb={'10px'}
          w={'100%'}
          justifyContent={'space-between'}
        >
          <Text fontSize={['24px', '26px', '30px']}>문의 게시판</Text>
        </Flex>
      </Flex>
      <Box>
        <Text fontSize={'xx-large'}>
          {BoardDetail ? BoardDetail.title : ''}
        </Text>
        <Box mt={'30px'}>
          <Flex gap={'10px'} mb={'20px'}>
            <Text>작성일자</Text>
            <Text>{BoardDetail ? formatDate(BoardDetail.post_date) : ''}</Text>
          </Flex>
          <Flex gap={'35px'}>
            <Text>내용</Text>
            <Textarea
              bg={'#fff'}
              maxW={'800px'}
              minH={'400px'}
              value={BoardDetail ? BoardDetail.content : ''}
              isReadOnly={true}
            ></Textarea>
          </Flex>
        </Box>
      </Box>
    </Box>
  );
};

export default DetailComponent;
