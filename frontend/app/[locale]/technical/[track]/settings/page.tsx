import API from '@/app/utils/api.server';
import BodyM from '@/app/components/bodyM';
import { getTranslations } from 'next-intl/server';
import ExtensionsManager from './extensions-manager';

export default async function TrackSettings() {
  const [{ data }, tr] = await Promise.all(
    [
      API.GET('/api/technical/extension/'),
      getTranslations("technicalSettingsPage")
    ]
  )
  const initialExtensions = data?.extensions || [];

  return (
    <BodyM>
      <div className="min-h-screen bg-gray-50/50 dark:bg-gray-950 py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-200">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{tr('title')}</h1>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {tr('desc')}
            </p>
          </div>
          <ExtensionsManager initialExtensions={initialExtensions} />
        </div>
      </div>
    </BodyM>
  );
}