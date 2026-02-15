import { onMounted, onUnmounted } from 'vue'

/**
 * 滚动入场动画组合式函数
 * 使用 Intersection Observer 检测元素是否进入视口，
 * 进入后添加 .animate-in 类触发 CSS 动画。
 *
 * 用法：
 * 1. 在组件中调用 useScrollAnimation()
 * 2. 在需要动画的元素上添加 class="scroll-animate"
 * 3. 可选：添加 data-delay="100" 控制延迟（毫秒）
 * 4. 可选：添加 data-direction="left|right|up|down" 控制方向
 */
export function useScrollAnimation() {
  let observer: IntersectionObserver | null = null

  onMounted(() => {
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target as HTMLElement
            const delay = el.dataset.delay || '0'
            el.style.transitionDelay = `${delay}ms`
            el.classList.add('animate-in')
            observer?.unobserve(el)
          }
        })
      },
      {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px',
      }
    )

    document.querySelectorAll('.scroll-animate').forEach((el) => {
      observer?.observe(el)
    })
  })

  onUnmounted(() => {
    observer?.disconnect()
  })
}
