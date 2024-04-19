import { ColorSchemeScript } from "@mantine/core";
import { Head, Html, Main, NextScript } from "next/document";

export default function Document() {
  const title = "Course Copilot | An AI Powered Assistant in Canvas";
  const description = "Canvas AI Copilot is a smart assistant in Canvas course rooms, designed to answer student questions effectively. This tool is part of a master thesis on how chatbots can enhance E-learning.";

  return (
    <Html lang="en">
      <Head>
        <meta name="title" content={title} />
        <meta name="description" content={description} />

        <link rel="shortcut icon" href="/favicon.svg" />

        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://copilot.openuni.ai/" />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:image" content="https://copilot.openuni.ai/og-image.jpg" />

        <meta property="twitter:card" content="summary_large_image" />
        <meta property="twitter:url" content="https://copilot.openuni.ai/" />
        <meta property="twitter:title" content={title} />
        <meta property="twitter:description" content={description} />
        <meta property="twitter:image" content="https://copilot.openuni.ai/og-image.jpg" />

        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <meta name="theme-color" content="#ffffff" />
        <meta name="color-scheme" content="light" />

        <ColorSchemeScript />
        <script
          dangerouslySetInnerHTML={{
            __html: `
            var _paq = window._paq = window._paq || [];
            /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
            _paq.push(['trackPageView']);
            _paq.push(['enableLinkTracking']);
            (function() {
              var u="//matomo.kthgpt.com/";
              _paq.push(['setTrackerUrl', u+'matomo.php']);
              _paq.push(['setSiteId', '3']);
              var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
              g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
            })();
          `,
          }}
        />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
