'use client';
import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Input,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Flex,
  InputGroup,
  InputRightElement,
  Stack,
  Text,
  Link,
} from '@chakra-ui/react';
import { FaSearch } from 'react-icons/fa';
import { useGetBoardQuery } from '@/app/api/useBoardClient';
import { formatDate } from '@/app/common/utils/dayformat';
import { useRouter } from 'next/navigation';

const BoardList = () => {
  const router = useRouter();
  const { data: boardList, isError: boardError } = useGetBoardQuery();
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    setPosts(boardList);
  }, [boardList]);

  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [filteredPosts, setFilteredPosts] = useState([]);
  const postsPerPage = 10;

  useEffect(() => {
    if (posts) {
      const results = posts.filter(
        (post) =>
          post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          post.author.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredPosts(results);
      setCurrentPage(1);
    }
  }, [searchTerm, posts]);

  // 현재 페이지의 게시글
  const indexOfLastPost = currentPage * postsPerPage;
  const indexOfFirstPost = indexOfLastPost - postsPerPage;
  const currentPosts = filteredPosts.slice(indexOfFirstPost, indexOfLastPost);

  // 페이지 변경 함수
  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  const onClickBoard = (idx) => {
    router.push(`/board/${idx}`);
  };

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
          <InputGroup width="300px">
            <Input
              placeholder="게시글 검색"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <InputRightElement>
              <FaSearch color="gray.500" />
            </InputRightElement>
          </InputGroup>
        </Flex>
      </Flex>

      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>글 번호</Th>
            <Th>제목</Th>
            <Th>작성시간</Th>
          </Tr>
        </Thead>
        <Tbody>
          {currentPosts
            .sort((a, b) => new Date(b.post_date) - new Date(a.post_date))
            .map((post) => (
              <Tr
                key={post.idx}
                onClick={() => onClickBoard(post.idx)}
                cursor={'pointer'}
              >
                <Td>{post.idx}</Td>
                <Td>{post.title}</Td>
                <Td>{formatDate(post.post_date)}</Td>
              </Tr>
            ))}
        </Tbody>
      </Table>

      <Flex justifyContent="space-between" alignItems="center" mt={5}>
        <Box flex={1}></Box>

        <Flex justifyContent="center" flex={1}>
          <Stack direction="row" spacing={2}>
            {Array.from(
              { length: Math.ceil(filteredPosts.length / postsPerPage) },
              (_, i) => (
                <Button
                  key={i}
                  onClick={() => paginate(i + 1)}
                  bg={'none'}
                  color={currentPage === i + 1 ? 'gray.500' : 'black'}
                >
                  {i + 1}
                </Button>
              )
            )}
          </Stack>
        </Flex>

        <Flex justifyContent="flex-end" flex={1}>
          <Button colorScheme="blue">
            <Link href="/board/create">글쓰기</Link>
          </Button>
        </Flex>
      </Flex>
    </Box>
  );
};

export default BoardList;
