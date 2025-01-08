'use client';
import React, { useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  Divider,
  Button,
  Collapse,
  Text,
  Link,
  HStack,
  Flex,
} from '@chakra-ui/react';
import {
  ChevronDownIcon,
  ChevronUpIcon,
  Avatar,
  UserIcon,
} from '@chakra-ui/icons';
import { FaUser } from 'react-icons/fa';
import { useAtom } from 'jotai';
import { userProfileAtom } from '@/app/atom/useUserAtom';
import { useUserData } from '@/app/api/useUserData';

const MenuItem = ({ title, subItems, href }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!subItems) {
    return (
      <Link href={href} style={{ textDecoration: 'none' }}>
        <Button
          variant="ghost"
          justifyContent="space-between"
          width="100%"
          py={2}
        >
          <Text>{title}</Text>
        </Button>
      </Link>
    );
  }

  return (
    <Box>
      <Button
        onClick={() => setIsOpen(!isOpen)}
        variant="ghost"
        justifyContent="space-between"
        width="100%"
        py={2}
      >
        {title}
        {isOpen ? <ChevronUpIcon /> : <ChevronDownIcon />}
      </Button>
      <Collapse in={isOpen} animateOpacity>
        <VStack align="stretch" pl={4} mt={2} spacing={2}>
          {subItems.map((item, index) => (
            <Link
              key={index}
              href={item.href}
              style={{ textDecoration: 'none' }}
            >
              <Text fontSize="sm">{item.title}</Text>
            </Link>
          ))}
        </VStack>
      </Collapse>
    </Box>
  );
};

const SideNavigation = () => {
  const menuItems = [
    {
      title: 'AI 면접 이력',
      href: '/myPage',
    },
    {
      title: '회원 정보',
      href: '/userinfo',
    },
    {
      title: '문의 게시판',
      href: '/board',
    },
  ];

  const { userProfileData } = useUserData();

  return (
    <Box as="nav" width="250px" height="70vh" p={4}>
      <VStack align="stretch" spacing={4}>
        <Box m={'0 auto'}>
          <Flex justifyContent={'center'} mb={'10px'}>
            <FaUser size={40} />
          </Flex>
          <Text fontSize={'24px'} textAlign={'center'}>
            {userProfileData.userInfo.name}
          </Text>
        </Box>
        <Heading size="lg" mb={2}>
          MyPage
        </Heading>
        <Divider border={'2px solid black'} opacity={'1'} />
        {menuItems.map((item, index) => (
          <MenuItem
            key={index}
            title={item.title}
            subItems={item.subItems}
            href={item.href}
          />
        ))}
      </VStack>
    </Box>
  );
};

export default SideNavigation;
