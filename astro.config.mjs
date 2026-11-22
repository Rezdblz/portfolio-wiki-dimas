// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://wiki.dimasreza.my.id',
  integrations: [
    starlight({
      title: 'Dimas Wiki',
      description: 'Dimas\' portfolio as a wiki: profile, projects, experience, and notes.',
      favicon: '/favicon.svg',
      editLink: {
        baseUrl: 'https://github.com/Rezdblz/portfolio-wiki-dimas/edit/main/',
      },
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/Rezdblz' },
        {
          icon: 'linkedin',
          label: 'LinkedIn',
          href: 'https://id.linkedin.com/in/dimas-ardhana',
        },
      ],
      sidebar: [
        { label: 'Home', link: '/' },
        { label: 'Profile', items: ['about', 'experience', 'skills'] },
        { label: 'Projects', items: [{ autogenerate: { directory: 'projects' } }] },
        { label: 'Notes', items: [{ autogenerate: { directory: 'notes' } }] },
        { label: 'Contact', items: ['contact'] },
      ],
    }),
  ],
});
