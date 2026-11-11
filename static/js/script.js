// ==========================================================================
// Reza.dev - 3D Interactive Engine, Themes & Scroll Animations
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {

    // ==========================================
    // 1. Multi-Theme Switcher (Sunset, Light, Emerald)
    // ==========================================
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeDropdown = document.getElementById('theme-dropdown');
    const themeOptions = document.querySelectorAll('.theme-option');

    // Retrieve saved theme or default to Cyber Emerald
    const savedTheme = localStorage.getItem('reza_site_theme') || 'emerald';
    applyTheme(savedTheme);

    if (themeToggleBtn && themeDropdown) {
        themeToggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            themeDropdown.classList.toggle('show');
        });

        document.addEventListener('click', (e) => {
            if (!themeDropdown.contains(e.target) && e.target !== themeToggleBtn) {
                themeDropdown.classList.remove('show');
            }
        });

        themeOptions.forEach(opt => {
            opt.addEventListener('click', () => {
                const selectedTheme = opt.getAttribute('data-theme-val');
                applyTheme(selectedTheme);
                themeDropdown.classList.remove('show');
            });
        });
    }

    function applyTheme(themeName) {
        document.documentElement.setAttribute('data-theme', themeName);
        localStorage.setItem('reza_site_theme', themeName);

        themeOptions.forEach(opt => {
            if (opt.getAttribute('data-theme-val') === themeName) {
                opt.classList.add('active');
            } else {
                opt.classList.remove('active');
            }
        });

        // Dynamic Android Status Bar Color (Theme Color Meta)
        const themeMetaColors = {
            sunset: '#120b24',
            light: '#f8fafc',
            emerald: '#080d0a'
        };
        const metaThemeColor = document.getElementById('meta-theme-color');
        if (metaThemeColor && themeMetaColors[themeName]) {
            metaThemeColor.setAttribute('content', themeMetaColors[themeName]);
        }

        // Update 3D Three.js colors if scene exists
        if (window.update3DThemeColors) {
            window.update3DThemeColors(themeName);
        }
    }

    // ==========================================
    // 2. Three.js 3D Interactive Floating Space
    // ==========================================
    const canvas = document.getElementById('webgl-canvas');
    if (canvas && typeof THREE !== 'undefined') {
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 35;

        const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // Color palettes for themes (ZERO BLUE)
        const themeColorMaps = {
            sunset: { main: 0xf43f5e, sec: 0xc084fc, accent: 0xf97316 },
            light: { main: 0xe11d48, sec: 0x9333ea, accent: 0xea580c },
            emerald: { main: 0x10b981, sec: 0xc084fc, accent: 0xf59e0b }
        };

        let currentColors = themeColorMaps[savedTheme] || themeColorMaps.sunset;

        // Group of floating 3D objects
        const objectsGroup = new THREE.Group();
        scene.add(objectsGroup);

        // 1. Floating Icosahedron
        const icoGeo = new THREE.IcosahedronGeometry(7, 1);
        const icoMat = new THREE.MeshBasicMaterial({
            color: currentColors.main,
            wireframe: true,
            transparent: true,
            opacity: 0.28
        });
        const icoMesh = new THREE.Mesh(icoGeo, icoMat);
        icoMesh.position.set(-16, 8, -5);
        objectsGroup.add(icoMesh);

        // 2. Floating Torus (Cyber Ring)
        const torusGeo = new THREE.TorusGeometry(8, 1.2, 12, 36);
        const torusMat = new THREE.MeshBasicMaterial({
            color: currentColors.sec,
            wireframe: true,
            transparent: true,
            opacity: 0.24
        });
        const torusMesh = new THREE.Mesh(torusGeo, torusMat);
        torusMesh.position.set(18, -10, -8);
        objectsGroup.add(torusMesh);

        // 3. Floating Octahedron (Security Core)
        const octGeo = new THREE.OctahedronGeometry(5, 0);
        const octMat = new THREE.MeshBasicMaterial({
            color: currentColors.accent,
            wireframe: true,
            transparent: true,
            opacity: 0.25
        });
        const octMesh = new THREE.Mesh(octGeo, octMat);
        octMesh.position.set(16, 14, -12);
        objectsGroup.add(octMesh);

        // 4. Ambient 3D Star / Particle Constellation
        const particleCount = 280;
        const particleGeo = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);

        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 110;
            positions[i + 1] = (Math.random() - 0.5) * 110;
            positions[i + 2] = (Math.random() - 0.5) * 80;
        }

        // Generate circular gradient texture for soft round particles (no square blocks)
        function createCircleTexture() {
            const pCanvas = document.createElement('canvas');
            pCanvas.width = 32;
            pCanvas.height = 32;
            const pCtx = pCanvas.getContext('2d');
            const pGrad = pCtx.createRadialGradient(16, 16, 0, 16, 16, 16);
            pGrad.addColorStop(0, 'rgba(255, 255, 255, 1)');
            pGrad.addColorStop(0.4, 'rgba(255, 255, 255, 0.75)');
            pGrad.addColorStop(1, 'rgba(255, 255, 255, 0)');
            pCtx.fillStyle = pGrad;
            pCtx.beginPath();
            pCtx.arc(16, 16, 16, 0, Math.PI * 2);
            pCtx.fill();
            return new THREE.CanvasTexture(pCanvas);
        }

        particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        const particleMat = new THREE.PointsMaterial({
            color: currentColors.sec,
            size: 1.4,
            map: createCircleTexture(),
            transparent: true,
            opacity: 0.45,
            depthWrite: false
        });
        const particleSystem = new THREE.Points(particleGeo, particleMat);
        objectsGroup.add(particleSystem);

        // Function to dynamically update 3D material colors and opacity on theme change
        window.update3DThemeColors = (theme) => {
            const colors = themeColorMaps[theme] || themeColorMaps.sunset;
            icoMat.color.setHex(colors.main);
            torusMat.color.setHex(colors.sec);
            octMat.color.setHex(colors.accent);
            particleMat.color.setHex(colors.sec);

            if (theme === 'light') {
                icoMat.opacity = 0.08;
                torusMat.opacity = 0.08;
                octMat.opacity = 0.08;
                particleMat.opacity = 0.28;
                particleMat.size = 1.1;
            } else {
                icoMat.opacity = 0.28;
                torusMat.opacity = 0.24;
                octMat.opacity = 0.25;
                particleMat.opacity = 0.45;
                particleMat.size = 1.4;
            }
        };

        // Initialize 3D theme colors and opacity for initial theme
        window.update3DThemeColors(savedTheme);

        // Mouse Parallax Effect
        let mouseX = 0;
        let mouseY = 0;
        let targetX = 0;
        let targetY = 0;

        window.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX - window.innerWidth / 2) * 0.0008;
            mouseY = (e.clientY - window.innerHeight / 2) * 0.0008;
        });

        // Animation Loop
        const clock = new THREE.Clock();
        function animate3D() {
            requestAnimationFrame(animate3D);
            const elapsedTime = clock.getElapsedTime();

            // Self rotations
            icoMesh.rotation.x = elapsedTime * 0.15;
            icoMesh.rotation.y = elapsedTime * 0.2;

            torusMesh.rotation.x = elapsedTime * 0.22;
            torusMesh.rotation.y = elapsedTime * 0.14;

            octMesh.rotation.y = elapsedTime * 0.25;
            octMesh.rotation.z = elapsedTime * 0.18;

            particleSystem.rotation.y = elapsedTime * 0.04;

            // Smooth camera tracking
            targetX += (mouseX - targetX) * 0.05;
            targetY += (mouseY - targetY) * 0.05;

            camera.position.x = targetX * 18;
            camera.position.y = -targetY * 18;

            // Camera depth reaction to scroll
            const scrollRatio = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight || 1);
            camera.position.z = 35 + scrollRatio * 15;

            camera.lookAt(scene.position);
            renderer.render(scene, camera);
        }
        animate3D();

        // Responsive Resize
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }

    // ==========================================
    // 3. 3D Tilt Interaction for Cards (.tilt-card)
    // ==========================================
    // Only enable on non-touch desktop screens to prevent touch scroll glitches
    const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0) || (window.innerWidth <= 768);
    if (!isTouchDevice) {
        const tiltCards = document.querySelectorAll('.tilt-card');
        tiltCards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = ((y - centerY) / centerY) * -10;
                const rotateY = ((x - centerX) / centerX) * 10;

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.025, 1.025, 1.025)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
            });
        });
    }

    // ==========================================
    // 4. Scroll Reveal Animations (IntersectionObserver)
    // ==========================================
    const revealElements = document.querySelectorAll('.reveal-on-scroll');
    if ('IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.12,
            rootMargin: '0px 0px -40px 0px'
        });

        revealElements.forEach(el => revealObserver.observe(el));
    } else {
        // Fallback for older browsers
        revealElements.forEach(el => el.classList.add('revealed'));
    }

    // ==========================================
    // 5. Scroll Progress Bar, Scroll Spy & Mobile Bottom Dock
    // ==========================================
    const progressBar = document.getElementById('scroll-progress-bar');
    const navbar = document.getElementById('navbar');
    const sections = document.querySelectorAll('section');
    const navItems = document.querySelectorAll('.nav-links .nav-item');
    const mobileNavItems = document.querySelectorAll('.mobile-nav-item');

    window.addEventListener('scroll', () => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / (docHeight || 1)) * 100;

        if (progressBar) {
            progressBar.style.width = `${scrollPercent}%`;
        }

        // Navbar blur on scroll
        if (navbar) {
            if (scrollTop > 40) {
                navbar.style.boxShadow = '0 12px 30px rgba(0, 0, 0, 0.35)';
            } else {
                navbar.style.boxShadow = 'none';
            }
        }

        // Section active link highlight
        let currentSectionId = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 120;
            const sectionHeight = section.offsetHeight;
            if (scrollTop >= sectionTop && scrollTop < sectionTop + sectionHeight) {
                currentSectionId = section.getAttribute('id');
            }
        });

        // Desktop Top Navbar active highlight
        navItems.forEach(item => {
            if (item.getAttribute('href') === `#${currentSectionId}`) {
                item.classList.add('active');
            } else if (item.getAttribute('href')?.startsWith('#')) {
                item.classList.remove('active');
            }
        });

        // Android / Mobile Bottom Nav active highlight
        mobileNavItems.forEach(item => {
            if (item.getAttribute('data-section') === currentSectionId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    });

    // Mobile Bottom Nav Smooth Scrolling with Header Offset (Only for in-page anchors)
    mobileNavItems.forEach(item => {
        item.addEventListener('click', (e) => {
            const href = item.getAttribute('href') || '';
            const targetSectionId = item.getAttribute('data-section');
            const targetSection = targetSectionId ? document.getElementById(targetSectionId) : null;
            
            // If the element exists on current page and href is a hash anchor, smooth scroll
            if (targetSection && href.startsWith('#')) {
                e.preventDefault();
                const headerOffset = 62;
                const elementPosition = targetSection.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });

                mobileNavItems.forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
            }
            // If it's a link to another page (e.g. /articles/), let browser navigate naturally
        });
    });

    // ==========================================
    // 5.2. Automatic Device Mode Detection
    // ==========================================
    function detectDeviceMode() {
        const isMobile = window.innerWidth <= 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        if (isMobile) {
            document.documentElement.classList.add('android-ui-mode');
            document.body.classList.add('android-ui-mode');
        } else {
            document.documentElement.classList.remove('android-ui-mode');
            document.body.classList.remove('android-ui-mode');
        }
    }
    detectDeviceMode();
    window.addEventListener('resize', detectDeviceMode);
    window.addEventListener('orientationchange', detectDeviceMode);

    // ==========================================
    // 6. Copy Email with Animated Feedback
    // ==========================================
    const copyEmailBtn = document.getElementById('copy-email-btn');
    const copyTooltip = document.getElementById('copy-tooltip');

    if (copyEmailBtn && copyTooltip) {
        copyEmailBtn.addEventListener('click', async () => {
            const email = copyEmailBtn.getAttribute('data-email') || 'reza1384mor@gmail.com';
            try {
                await navigator.clipboard.writeText(email);
                copyTooltip.classList.add('show');
                setTimeout(() => copyTooltip.classList.remove('show'), 2200);
            } catch (err) {
                const textArea = document.createElement('textarea');
                textArea.value = email;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);

                copyTooltip.classList.add('show');
                setTimeout(() => copyTooltip.classList.remove('show'), 2200);
            }
        });
    }

    // ==========================================
    // 7. Mobile Menu Toggle
    // ==========================================
    const menuToggle = document.getElementById('menu-toggle');
    const navLinks = document.getElementById('nav-links');

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('open');
            const icon = menuToggle.querySelector('i');
            if (navLinks.classList.contains('open')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-xmark');
            } else {
                icon.classList.remove('fa-xmark');
                icon.classList.add('fa-bars');
            }
        });

        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('open');
                const icon = menuToggle.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-xmark');
                    icon.classList.add('fa-bars');
                }
            });
        });
    }

    // ==========================================
    // 8. Auto-dismiss Alert Messages
    // ==========================================
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-12px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});
