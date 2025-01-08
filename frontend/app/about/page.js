import { Box, Flex } from '@chakra-ui/react';
import Header from '../common/components/header';
import SideNavigation from '../myPage/components/navigation';
import Section from './components/section';
import Container from '../common/components/container';

function About() {
  return (
    <Container>
      <Header />
      <Section />
    </Container>
  );
}

export default About;
