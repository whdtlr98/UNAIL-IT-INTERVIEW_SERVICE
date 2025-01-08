import React from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  Text,
  useDisclosure,
} from '@chakra-ui/react';

function WithDrawModal({ isOpen, onClose }) {
  const handleDeleteAccount = () => {
    console.log('회원 탈퇴 진행');
    onClose();
  };

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>탈퇴 전 다시 한번만 확인해주세요</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text>
              회원 탈퇴 시 모든 개인정보 데이터는 삭제됩니다 <br />
              (소셜 로그인 정보 및 면접 이력 데이터) <br />
              <strong>정말 탈퇴 하시겠습니까?</strong>
            </Text>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme='red' mr={3} onClick={handleDeleteAccount}>
              탈퇴하기
            </Button>
            <Button variant='ghost' onClick={onClose}>
              취소
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
}

export default WithDrawModal;
