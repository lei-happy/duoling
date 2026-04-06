/**
 * 本地上传图片：读取像素尺寸、检测是否存在透明像素（用于规范 Logo/封面图）
 */

export function readImageFileDimensions(
  file: File
): Promise<{ width: number; height: number }> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve({ width: img.naturalWidth, height: img.naturalHeight });
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error('无法读取图片'));
    };
    img.src = url;
  });
}

/** 是否存在半透明/全透明像素；不支持检测时返回 null */
export async function imageFileHasTransparency(
  file: File
): Promise<boolean | null> {
  try {
    const bmp = await createImageBitmap(file);
    try {
      const canvas = document.createElement('canvas');
      canvas.width = bmp.width;
      canvas.height = bmp.height;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) return null;
      ctx.drawImage(bmp, 0, 0);
      const { data } = ctx.getImageData(0, 0, canvas.width, canvas.height);
      for (let i = 3; i < data.length; i += 4) {
        if (data[i]! < 255) return true;
      }
      return false;
    } finally {
      bmp.close();
    }
  } catch {
    return null;
  }
}
