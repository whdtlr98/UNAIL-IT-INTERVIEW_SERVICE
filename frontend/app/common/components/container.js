import { Box } from '@chakra-ui/react';
import React from 'react';

const Container = ({ children }) => {
  return (
    <Box
      w="100%"
      minH="100vh"
      backgroundImage="linear-gradient(to bottom, #F5F6FE, #DFE2FB, #EBEEFC)"
    >
      {children}
    </Box>
  );
};

export default Container;
