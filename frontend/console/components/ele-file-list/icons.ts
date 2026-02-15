import type { IconItem } from './types';

/**
 * 本地小尺寸图标
 */
export const localSmallIcons: IconItem[] = [
  {
    icon: '/ele-file-list/ic_file_misc_sm.png',
    type: 'file'
  },
  {
    icon: '/ele-file-list/ic_file_folder_sm.png',
    type: 'dir'
  },
  {
    icon: '/ele-file-list/ic_file_code_sm.png',
    suffixes: [
      '.java',
      '.js',
      '.css',
      '.vue',
      '.ts',
      '.tsx',
      '.scss',
      '.less',
      '.c',
      '.cpp',
      '.cs',
      '.jsp',
      '.php',
      '.asp',
      '.py',
      '.go',
      '.kt',
      '.lua'
    ]
  },
  {
    icon: '/ele-file-list/ic_file_htm_sm.png',
    suffixes: ['.html', '.htm']
  },
  {
    icon: '/ele-file-list/ic_file_text_sm.png',
    suffixes: ['.txt']
  },
  {
    icon: '/ele-file-list/ic_file_pdf_sm.png',
    suffixes: ['.pdf']
  },
  {
    icon: '/ele-file-list/ic_file_word_sm.png',
    suffixes: ['.doc', '.docx']
  },
  {
    icon: '/ele-file-list/ic_file_excel_sm.png',
    suffixes: ['.xls', '.xlsx']
  },
  {
    icon: '/ele-file-list/ic_file_ppt_sm.png',
    suffixes: ['.ppt', '.pptx']
  },
  {
    icon: '/ele-file-list/ic_file_visio_sm.png',
    suffixes: ['.vsd']
  },
  {
    icon: '/ele-file-list/ic_file_ps_sm.png',
    suffixes: ['.psd']
  },
  {
    icon: '/ele-file-list/ic_file_cad_sm.png',
    suffixes: ['.dwg']
  },
  {
    icon: '/ele-file-list/ic_file_flash_sm.png',
    suffixes: ['.swf']
  },
  {
    icon: '/ele-file-list/ic_file_music_sm.png',
    suffixes: ['.mp3', '.wav']
  },
  {
    icon: '/ele-file-list/ic_file_video_sm.png',
    suffixes: ['.mp4', '.rmvb', '.flv', '.avi', '.3gp']
  },
  {
    icon: '/ele-file-list/ic_file_picture_sm.png',
    suffixes: [
      '.png',
      '.jpg',
      '.jpeg',
      '.gif',
      '.bmp',
      '.svg',
      '.webp',
      '.tiff'
    ]
  },
  {
    icon: '/ele-file-list/ic_file_fonts_sm.png',
    suffixes: ['.ttf', '.woff']
  },
  {
    icon: '/ele-file-list/ic_file_bt_sm.png',
    suffixes: ['.torrent']
  },
  {
    icon: '/ele-file-list/ic_file_android_sm.png',
    suffixes: ['.apk']
  },
  {
    icon: '/ele-file-list/ic_file_exe_sm.png',
    suffixes: ['.exe']
  },
  {
    icon: '/ele-file-list/ic_file_ipa_sm.png',
    suffixes: ['.ipa', '.dmg']
  },
  {
    icon: '/ele-file-list/ic_file_zip_sm.png',
    suffixes: ['.zip', '.rar', '.7z']
  }
];

/**
 * 本地图标
 */
export const localIcons: IconItem[] = localSmallIcons.map((d) => {
  return { ...d, icon: d.icon.replace('_sm.png', '.png') };
});

/**
 * 默认小尺寸图标
 */
export const smallIcons: IconItem[] = localSmallIcons.map((d) => {
  return {
    ...d,
    icon: d.icon.replace(
      '/ele-file-list/',
      'https://cdn.eleadmin.com/20200609/'
    )
  };
});

/**
 * 默认图标
 */
export const icons: IconItem[] = smallIcons.map((d) => {
  return { ...d, icon: d.icon.replace('_sm.png', '.png') };
});
