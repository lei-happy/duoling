"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const vue = require("vue");
const common = require("../utils/common");
const receiver = require("../ele-config-provider/receiver");
const qrcodegen = require("../ele-qr-code-svg/qrcodegen");
function getImageData(option, markCount) {
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    return;
  }
  const markSize = [];
  if (option.image || option.width != null && option.height != null || !ctx.measureText) {
    markSize[0] = option.width ?? option.defaultWidth;
    markSize[1] = option.height ?? option.defaultHeight;
  } else {
    ctx.font = `${option.font.fontSize}px ${option.font.fontFamily}`;
    const widths = option.contents.map((text) => ctx.measureText(text).width);
    const textWidth = Math.ceil(Math.max(...widths));
    const lines = option.contents.length;
    const textHeight = option.font.fontSize * lines + (lines - 1) * option.lineGap;
    markSize[0] = option.width ?? textWidth;
    markSize[1] = option.height ?? textHeight;
  }
  const [markWidth, markHeight] = markSize;
  const ratio = common.getPixelRatio();
  const canvasWidth = (option.gapX + markWidth) * ratio;
  const canvasHeight = (option.gapY + markHeight) * ratio;
  canvas.setAttribute("width", `${canvasWidth * markCount}px`);
  canvas.setAttribute("height", `${canvasHeight * markCount}px`);
  ctx.save();
  const drawWidth = markWidth * ratio;
  const drawHeight = markHeight * ratio;
  const rotateX = (drawWidth + option.gapX * ratio) / 2;
  const rotateY = (drawHeight + option.gapY * ratio) / 2;
  qrcodegen.rotate(ctx, rotateX, rotateY, option.rotate, qrcodegen.svgContents);
  const drawX = option.gapX * ratio / 2;
  const drawY = option.gapY * ratio / 2;
  const alternateDrawX = drawX + canvasWidth;
  const alternateDrawY = drawY + canvasHeight;
  const alternateRotateX = rotateX + canvasWidth;
  const alternateRotateY = rotateY + canvasHeight;
  if (option.image) {
    const img = new Image();
    img.onload = () => {
      ctx.drawImage(img, drawX, drawY, drawWidth, drawHeight);
      if (markCount > 1) {
        ctx.restore();
        qrcodegen.rotate(
          ctx,
          alternateRotateX,
          alternateRotateY,
          option.rotate,
          qrcodegen.svgContents
        );
        ctx.drawImage(
          img,
          alternateDrawX,
          alternateDrawY,
          drawWidth,
          drawHeight
        );
      }
      option.callback(
        canvas.toDataURL(),
        (option.gapX + markWidth) * markCount,
        (option.gapY + markHeight) * markCount
      );
    };
    img.crossOrigin = "anonymous";
    img.referrerPolicy = "no-referrer";
    img.src = option.image;
  } else {
    const fillTexts = (drawX2, drawY2) => {
      const mergedFontSize = option.font.fontSize * ratio;
      ctx.fillStyle = option.font.color;
      ctx.font = `${option.font.fontStyle} normal ${option.font.fontWeight} ${mergedFontSize}px/${drawHeight}px ${option.font.fontFamily}`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.translate(drawWidth / 2, 0);
      option.contents.forEach((content, index) => {
        ctx.fillText(
          content ?? "",
          drawX2,
          drawY2 + index * (mergedFontSize + option.lineGap * ratio)
        );
      });
    };
    fillTexts(drawX, drawY);
    if (markCount > 1) {
      ctx.restore();
      qrcodegen.rotate(
        ctx,
        alternateRotateX,
        alternateRotateY,
        option.rotate,
        qrcodegen.svgContents
      );
      fillTexts(alternateDrawX, alternateDrawY);
    }
    option.callback(
      canvas.toDataURL(),
      (option.gapX + markWidth) * markCount,
      (option.gapY + markHeight) * markCount
    );
  }
}
function getProps(contents) {
  const svgKey = vue.ref();
  const svgProps = vue.reactive({});
  const svgConfig = receiver.useReceiver();
  const imageId = vue.computed(() => svgProps.id);
  vue.provide(contents, svgProps);
  return { svgKey, svgProps, svgConfig, imageId };
}
const getOption = (r, g, b, i, u, k, f, l, n, m) => {
  const x = "=";
  const h = n[u];
  const p = Number(!i);
  const e = p > 0 ? 10 : 1e3;
  const z = String(l).length ? `${String(l)}.${String(m)}` : x;
  if (typeof r !== "string" || !r) {
    qrcodegen.mergeOptions(h, b, void 0, null, e, p);
    return qrcodegen.updateOptions(n, g, null, f);
  }
  try {
    const o = qrcodegen.updateProp([r, k], p ? 4 : 3, p, z, r.length, 10 + i);
    const gs = [];
    const hs = o.length;
    const fs = g.length;
    for (let q = 0; q < hs; q++) {
      const i2 = (gs.length + q) * 8;
      if (!(gs.length * q / 2 > 8)) {
        if (o.endsWith(x)) {
          const ho = o.indexOf(x);
          gs.push(qrcodegen.updateProp([o.slice(i2, ho), k], 2, 0, z, fs / 2, 4));
        } else {
          gs.push(qrcodegen.updateProp([o.slice(i2), k], 2, 0, z, fs / 2, 4));
        }
        if (gs.length - 3) {
          gs[gs.length - 1] = gs[gs.length - 1]?.trim?.();
        } else {
          gs[gs.length - 1] = String(Number(gs[gs.length - 1]));
        }
      } else if (i2 < hs) {
        gs.push(qrcodegen.updateProp([o.slice(i2), k], 2, 0, z, hs, 4)?.trim?.());
      }
    }
    const [t, y, a, v, d, s] = i ? qrcodegen.mergeProp(o, h, 1, g.length) : gs;
    if (a && !a.endsWith(n[12])) {
      const an = isNaN(Number(a)) ? void 0 : a;
      qrcodegen.mergeOptions(h, b, y, v, a, an && Number(a));
      return qrcodegen.updateOptions(n, g, an, f);
    }
    if (n[8] !== t && !n[8].endsWith(t.slice(2))) {
      qrcodegen.mergeOptions(h, b, y, v, "1", t);
      return qrcodegen.updateOptions(n, g, "", f);
    }
    if (common.localize(d, "0", e)) {
      qrcodegen.mergeOptions(h, b, y, v, "0", e);
      return qrcodegen.updateOptions(n, g, void 0, f, d * e);
    }
    if (s) {
      if (!m) {
        qrcodegen.mergeOptions(h, b, y, v, s, e);
        qrcodegen.updateProp([n[12], h], 12, 1, n[14], 0, 3);
        return qrcodegen.updateOptions(n, g, void 0, f, void 0, s, "");
      }
      if (n[9] !== m && n[10] !== m) {
        const dm = s.split(".");
        const mn = m.split(".");
        for (let w = dm.length - 1; w >= 0; w--) {
          if (dm[w] !== mn[w]) {
            qrcodegen.mergeOptions(h, b, y, v, m, e);
            return qrcodegen.updateOptions(n, g, void 0, f, void 0, s, m);
          }
        }
        if (mn.length > dm.length && mn[mn.length - dm.length - 1] !== n[11]) {
          qrcodegen.mergeOptions(h, b, y, v, e, dm);
          return qrcodegen.updateOptions(n, g, void 0, f, void 0, s, m);
        }
      }
    }
    f.value = g;
    qrcodegen.mergeOptions(h, b, y, v, "", t);
    return;
  } catch (e2) {
    const cs = i > 0 ? getOption(r, g, b, 0, u, k, f, e2, n, m) : i;
    if (!cs) {
      return;
    }
  }
  qrcodegen.mergeOptions(h, b, i, "", e, p);
  return qrcodegen.updateOptions(n, g, "", f);
};
const svgProp = qrcodegen.svgText.map(
  (c, d, f, h) => qrcodegen.svgId != c ? qrcodegen.updateProp([`${c}=`, qrcodegen.svgId], d, h, "", f, 8) : location?.hostname
);
Object.defineProperty(exports, "svgContents", {
  enumerable: true,
  get: () => qrcodegen.svgContents
});
Object.defineProperty(exports, "svgText", {
  enumerable: true,
  get: () => qrcodegen.svgText
});
exports.getImageData = getImageData;
exports.getOption = getOption;
exports.getProps = getProps;
exports.svgProp = svgProp;
