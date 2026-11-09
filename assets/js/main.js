// 每日新闻 - 交互脚本
// 可扩展：分类筛选、懒加载、无限滚动、搜索等

(function() {
    'use strict';

    // DOM 加载完成后初始化
    document.addEventListener('DOMContentLoaded', function() {
        initCategoryFilter();
        initSmoothScroll();
        initLazyImages();
        console.log('每日新闻站点已加载');
    });

    // 分类导航筛选（预留功能）
    function initCategoryFilter() {
        const navLinks = document.querySelectorAll('.nav a');
        const heroArticle = document.querySelector('.hero-article');
        const newsCards = document.querySelectorAll('.news-card');
        const listItems = document.querySelectorAll('.list-item');

        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const category = this.textContent.trim();
                
                // 历史链接需要正常跳转，不阻止默认行为
                if (category === '历史') {
                    return;
                }
                
                e.preventDefault();

                // 更新激活状态
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');

                // 这里可以接入真实 API 筛选
                console.log('筛选分类:', category);

                // 演示：仅高亮显示对应分类
                if (category === '首页') {
                    [heroArticle, ...newsCards, ...listItems].forEach(el => {
                        if (el) el.style.display = '';
                    });
                } else {
                    // 实际项目中应请求 API 获取对应分类数据
                    console.log('需对接后端 API 获取', category, '分类数据');
                }
            });
        });
    }

    // 平滑滚动
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;

                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }

    // 图片懒加载（为未来真实图片预留）
    function initLazyImages() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                        }
                        observer.unobserve(img);
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    // 暴露全局方法供扩展
    window.NewsApp = {
        loadCategory: function(category) {
            console.log('加载分类:', category);
            // TODO: 对接真实 API
        },
        refresh: function() {
            console.log('刷新新闻列表');
            // TODO: 对接真实 API
        }
    };
})();