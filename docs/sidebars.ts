import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: ['getting-started/quickstart', 'getting-started/installation'],
    },
    {
      type: 'category',
      label: 'Architecture',
      items: ['architecture/overview', 'architecture/services', 'architecture/events'],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: ['api/triage', 'api/concepts', 'api/exercises', 'api/execution'],
    },
    {
      type: 'category',
      label: 'Development',
      items: ['development/skills', 'development/contributing'],
    },
  ],
};

export default sidebars;
