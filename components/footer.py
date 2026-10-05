"""Professional EmployaAI website footers.

Full-width, translucent glassmorphism that lets the campus background shine through.
Four-column layout: brand + social, Quick Links, Support, Stay Updated with email subscribe.
Bottom copyright bar with policy links.
"""

from __future__ import annotations

from components.html import render_html


def render_footer(variant: str = "app") -> None:
    """Render an elegant EmployaAI footer.
    
    Variants:
        - 'landing': Elegant, four-column public footer matching the reference design
                     with social icons, link arrows, and an email subscribe section.
        - 'app': Compact, minimal single-line footer for protected screens.
    """
    if variant == "landing":
        render_html("""
        <footer class="site-footer">
            <div class="footer-content">
                <div class="ea-footer-grid">
                    <!-- Column 1: Brand + description + social -->
                    <div>
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
                            <div style="width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px; color: #FFFFFF;">E</div>
                            <div>
                                <div style="font-weight: 800; font-size: 20px; color: rgba(255,255,255,0.95); letter-spacing: -0.02em;">EmployAI</div>
                                <div style="color: rgba(255,255,255,0.60); font-size: 10px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;">AI EMPLOYABILITY PLATFORM</div>
                            </div>
                        </div>
                        <div style="color: rgba(255,255,255,0.70); font-size: 13px; line-height: 1.65; max-width: 300px; margin-bottom: 18px;">
                            Empowering students to assess skills, bridge gaps and build a personalized career roadmap with real-world opportunities.
                        </div>
                        <!-- Social icons -->
                        <div style="display: flex; gap: 10px;">
                            <a href="#" class="ea-social-icon" aria-label="LinkedIn">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                            </a>
                            <a href="#" class="ea-social-icon" aria-label="Instagram">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
                            </a>
                            <a href="#" class="ea-social-icon" aria-label="YouTube">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
                            </a>
                            <a href="#" class="ea-social-icon" aria-label="X (Twitter)">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                            </a>
                        </div>
                    </div>

                    <!-- Column 2: Quick Links -->
                    <div>
                        <div class="ea-footer-col-title">Quick Links</div>
                        <div style="display: flex; flex-direction: column; gap: 9px; font-size: 13.5px;">
                            <span class="ea-footer-link-arrow" onclick="window.scrollTo({top:0,behavior:'smooth'})"><span>Assessment</span><span class="ea-arrow">›</span></span>
                            <span class="ea-footer-link-arrow"><span>Skill Gap Analysis</span><span class="ea-arrow">›</span></span>
                            <span class="ea-footer-link-arrow"><span>Career Roadmap</span><span class="ea-arrow">›</span></span>
                            <span class="ea-footer-link-arrow"><span>Jobs & Internships</span><span class="ea-arrow">›</span></span>
                            <span class="ea-footer-link-arrow"><span>Reports</span><span class="ea-arrow">›</span></span>
                        </div>
                    </div>

                    <!-- Column 3: Support -->
                    <div>
                        <div class="ea-footer-col-title">Support</div>
                        <div style="display: flex; flex-direction: column; gap: 9px; font-size: 13.5px;">
                            <span class="ea-footer-link-arrow"><span>Help Center</span><span class="ea-arrow">›</span></span>
                            <span class="ea-footer-link-arrow"><span>Contact Us</span><span class="ea-arrow">›</span></span>
                            <span class="ea-footer-link-arrow"><span>Privacy Policy</span><span class="ea-arrow">›</span></span>
                            <span class="ea-footer-link-arrow"><span>Terms of Service</span><span class="ea-arrow">›</span></span>
                            <span class="ea-footer-link-arrow"><span>Accessibility</span><span class="ea-arrow">›</span></span>
                            <span class="ea-footer-link-arrow"><span>FAQ</span><span class="ea-arrow">›</span></span>
                        </div>
                    </div>

                    <!-- Column 4: Stay Updated -->
                    <div>
                        <div class="ea-footer-col-title">Stay Updated</div>
                        <div style="color: rgba(255,255,255,0.70); font-size: 13px; line-height: 1.6; margin-bottom: 16px;">
                            Get the latest updates, career insights and new opportunities.
                        </div>
                        <div class="ea-subscribe-row">
                            <div class="ea-subscribe-input-wrap">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><path d="m22 6-10 7L2 6"/></svg>
                                <input type="email" placeholder="Enter your email address" class="ea-subscribe-input" readonly />
                            </div>
                            <button class="ea-subscribe-btn">Subscribe</button>
                        </div>
                    </div>
                </div>

                <!-- Bottom bar -->
                <div style="height: 1px; background: rgba(255, 255, 255, 0.10); margin: 28px 0 16px 0;"></div>
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; font-size: 12px; color: rgba(255,255,255,0.65);">
                    <div>© 2026 EmployAI. All rights reserved.</div>
                    <div style="display: flex; gap: 20px; align-items: center;">
                        <span class="ea-footer-link">Privacy Policy</span>
                        <span style="opacity: 0.3;">|</span>
                        <span class="ea-footer-link">Terms of Service</span>
                        <span style="opacity: 0.3;">|</span>
                        <span class="ea-footer-link">Accessibility</span>
                    </div>
                </div>
            </div>
        </footer>
        <style>
        .site-footer {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            z-index: 999 !important;
            margin: 0 !important;
            line-height: 1.5 !important;
            background: rgba(18, 12, 40, 0.92) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border-top: 1px solid rgba(255, 255, 255, 0.10) !important;
            border-left: none !important;
            border-right: none !important;
            border-bottom: none !important;
            border-radius: 0 !important;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.3) !important;
            padding: 36px 0 18px 0 !important;
            box-sizing: border-box !important;
        }
        /* Push Streamlit wrappers around the footer to the very bottom with no gaps */
        div:has(> .site-footer),
        [data-testid="element-container"]:has(.site-footer),
        [data-testid="stMarkdownContainer"]:has(.site-footer) {
            margin: 0 !important;
            padding: 0 !important;
        }
        .site-footer .footer-content {
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 0 32px !important;
            box-sizing: border-box !important;
        }
        .ea-footer-grid {
            display: grid !important;
            grid-template-columns: 1.4fr 1.2fr 1.2fr 1.5fr !important;
            gap: 24px !important;
            margin-bottom: 0 !important;
        }
        .ea-footer-col-title {
            color: #FFFFFF !important;
            font-size: 15px !important;
            font-weight: 700 !important;
            margin-bottom: 16px !important;
            letter-spacing: 0.01em !important;
        }
        .ea-footer-link {
            color: rgba(255, 255, 255, 0.80) !important;
            text-decoration: none !important;
            cursor: pointer !important;
            transition: color 0.18s ease !important;
        }
        .ea-footer-link:hover {
            color: #FFFFFF !important;
            text-decoration: underline !important;
        }
        .ea-footer-link-arrow {
            color: rgba(255, 255, 255, 0.80) !important;
            text-decoration: none !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            transition: color 0.18s ease !important;
        }
        .ea-footer-link-arrow:hover {
            color: #FFFFFF !important;
        }
        .ea-footer-link-arrow .ea-arrow {
            color: rgba(255,255,255,0.45);
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s ease, color 0.2s ease;
        }
        .ea-footer-link-arrow:hover .ea-arrow {
            color: #FFFFFF;
            transform: translateX(3px);
        }
        .ea-social-icon {
            width: 36px; height: 36px;
            border-radius: 50%;
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.15);
            display: flex; align-items: center; justify-content: center;
            color: rgba(255,255,255,0.85);
            text-decoration: none;
            transition: background 0.2s ease, transform 0.2s ease;
        }
        .ea-social-icon:hover {
            background: rgba(139,92,246,0.4);
            transform: translateY(-2px);
            color: #FFFFFF;
        }
        .ea-subscribe-row {
            display: flex;
            gap: 0;
            align-items: stretch;
        }
        .ea-subscribe-input-wrap {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 10px 0 0 10px;
            padding: 0 12px;
            min-height: 40px;
        }
        .ea-subscribe-input {
            background: transparent !important;
            border: none !important;
            outline: none !important;
            color: rgba(255,255,255,0.65) !important;
            font-size: 12.5px !important;
            width: 100% !important;
            padding: 8px 0 !important;
            -webkit-text-fill-color: rgba(255,255,255,0.65) !important;
        }
        .ea-subscribe-input::placeholder {
            color: rgba(255,255,255,0.40) !important;
            -webkit-text-fill-color: rgba(255,255,255,0.40) !important;
        }
        .ea-subscribe-btn {
            background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%) !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            border: none !important;
            border-radius: 0 10px 10px 0 !important;
            padding: 0 20px !important;
            cursor: pointer !important;
            transition: opacity 0.2s ease !important;
            white-space: nowrap !important;
        }
        .ea-subscribe-btn:hover {
            opacity: 0.9 !important;
        }
        @media (max-width: 900px) {
            .ea-footer-grid {
                grid-template-columns: 1fr 1fr !important;
                gap: 28px !important;
            }
        }
        @media (max-width: 560px) {
            .ea-footer-grid {
                grid-template-columns: 1fr !important;
                gap: 24px !important;
            }
            .site-footer .footer-content {
                padding: 0 20px !important;
            }
        }
        </style>
        """)
    else:
        # Compact application footer for authenticated pages (Dashboard, Profile, Assessment, etc.)
        render_html("""
        <footer class="ea-app-footer" style="margin-top: 36px; padding: 14px 20px; border-top: 1px solid #E5E1F0; background: transparent; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 22px; height: 22px; border-radius: 6px; background: #7C3AED; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 12px; color: #FFF;">E</div>
                <span style="font-weight: 700; font-size: 13px; color: #211C36;">EmployAI</span>
                <span style="color: #7C7490; font-size: 12px;">· AI-Powered Employability Platform</span>
            </div>
            <div style="display: flex; align-items: center; gap: 14px; font-size: 12px; color: #7C7490;">
                <span>© 2026 EmployAI</span>
                <span>•</span>
                <span>Privacy</span>
                <span>•</span>
                <span>Terms</span>
                <span>•</span>
                <span>Support</span>
            </div>
        </footer>
        """)
