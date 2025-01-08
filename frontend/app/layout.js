'use client';
import { ChakraProvider } from '@chakra-ui/react';
import 'regenerator-runtime/runtime';
import './global.css';
import Head from 'next/head';
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import UserGuard from './common/utils/userGuard';
import { UserProvider } from './common/utils/userProvider';

// const geistSans = localFont({
//   src: "./fonts/GeistVF.woff",
//   variable: "--font-geist-sans",
//   weight: "100 900",
// });
// const geistMono = localFont({
//   src: "./fonts/GeistMonoVF.woff",
//   variable: "--font-geist-mono",
//   weight: "100 900",
// });

const queryClient = new QueryClient();

// export const metadata = {
//   title: 'Unail,IT',
//   description: '당신의 합격을 기원합니다.',
//   icons: {
//     icon: '/favicon.ico',
//   },
// };

export default function RootLayout(props) {
  const { children } = props;
  return (
    <html>
      <Head>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <body suppressHydrationWarning={true}>
        <QueryClientProvider client={queryClient}>
          <ChakraProvider>
            <UserProvider>
              {children}
            </UserProvider>
          </ChakraProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}
