import { atom } from 'jotai';
// 로딩 여부 atom
export const isUserLoadedAtom = atom(false);

// Token Data
export const accessTokenAtom = atom('');
export const refreshTokenAtom = atom('');

export const userProfileAtom = atom({
  userInfo: {
    name: '',
    email: '',
  },
});
