/**
 * Copyright (c) 2017-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

const React = require('react');

const CompLibrary = require('../../core/CompLibrary.js');

const MarkdownBlock = CompLibrary.MarkdownBlock; /* Used to read markdown */
const Container = CompLibrary.Container;
const GridBlock = CompLibrary.GridBlock;

class HomeSplash extends React.Component {
  render() {
    const {siteConfig, language = ''} = this.props;
    const {baseUrl, docsUrl} = siteConfig;
    const docsPart = `${docsUrl ? `${docsUrl}/` : ''}`;
    const langPart = `${language ? `${language}/` : ''}`;
    const docUrl = doc => `${baseUrl}${docsPart}${langPart}${doc}`;

    const SplashContainer = props => (
      <div className="homeContainer">
        <div className="homeSplashFade">
          <div className="wrapper homeWrapper">{props.children}</div>
        </div>
      </div>
    );

    const Logo = props => (
      <div className="projectLogo">
        <img src={props.img_src} alt="Project Logo" />
      </div>
    );

    const ProjectTitle = props => (
      <h2 className="projectTitle">
        {props.title}
        <small>{props.tagline}</small>
      </h2>
    );

    const PromoSection = props => (
      <div className="section promoSection">
        <div className="promoRow">
          <div className="pluginRowBlock">{props.children}</div>
        </div>
      </div>
    );

    const Button = props => (
      <div className="pluginWrapper buttonWrapper">
        <a className="button" href={props.href} target={props.target}>
          {props.children}
        </a>
      </div>
    );

    return (
      <SplashContainer>
        <div className="inner">
          <ProjectTitle tagline={siteConfig.tagline} title={siteConfig.title} />
          <Logo img_src={`${baseUrl}img/undraw_result.svg`} />
          <PromoSection>
            <Button href={docUrl('quickstart.html')}>Docs</Button>
            <Button href={siteConfig.repoUrl}>Github</Button>
          </PromoSection>
        </div>
      </SplashContainer>
    );
  }
}

class Index extends React.Component {
  render() {
    const {config: siteConfig, language = ''} = this.props;
    const {baseUrl} = siteConfig;

    const Block = props => (
      <Container
        padding={['bottom', 'top']}
        id={props.id}
        background={props.background}>
        <GridBlock
          align="center"
          contents={props.children}
          layout={props.layout}
        />
      </Container>
    );

    const Features = () => (
      <Block layout="fourColumn">
        {[
          {
            content: 'Run end-to-end tests as they would work in the real world',
            image: `${baseUrl}img/undraw_code_review.svg`,
            imageAlign: 'top',
            title: 'Black Box Testing',
          },
          {
            content: 'Multiple built-in runners to test common services with the option to add your own',
            image: `${baseUrl}img/undraw_operating_system.svg`,
            imageAlign: 'top',
            title: 'Covers Complex Use Cases',
          },
          {
            content: 'Spin up a swarm of test runners to make sure your system can operate at scale',
            image: `${baseUrl}img/undraw_progress_data.svg`,
            imageAlign: 'top',
            title: 'Built For Load Testing',
          },
        ]}
      </Block>
    );

    const BigFeature1 = () => (
      <Block background="light">
        {[
          {
            content:
              'Run end-to-end tests as they would work in the real world',
            image: `${baseUrl}img/undraw_code_review.svg`,
            imageAlign: 'right',
            title: 'Black Box Testing',
          },
        ]}
      </Block>
    );

    const BigFeature2 = () => (
      <Block background="dark">
        {[
          {
            content:
              'Spin up a swarm of test runners to make sure your system can operate at scale',
            image: `${baseUrl}img/undraw_operating_system.svg`,
            imageAlign: 'left',
            title: 'Covers Complex Use Cases',
          },
        ]}
      </Block>
    );

    const BigFeature3 = () => (
      <Block>
        {[
          {
            content:
              'Spin up a swarm of test runners to make sure your system can operate at scale',
            image: `${baseUrl}img/undraw_progress_data.svg`,
            imageAlign: 'right',
            title: 'Built For Load Testing',
          },
        ]}
      </Block>
    );

    const Showcase = () => {
      if ((siteConfig.users || []).length === 0) {
        return null;
      }

      const showcase = siteConfig.users
        .filter(user => user.pinned)
        .map(user => (
          <a href={user.infoLink} key={user.infoLink}>
            <img src={user.image} alt={user.caption} title={user.caption} />
          </a>
        ));

      const pageUrl = page => baseUrl + (language ? `${language}/` : '') + page;

      return (
        <div className="productShowcaseSection paddingBottom">
          <h2>Who is Using This?</h2>
          <p>This project is used by all these people</p>
          <div className="logos">{showcase}</div>
          <div className="more-users">
            <a className="button" href={pageUrl('users.html')}>
              More {siteConfig.title} Users
            </a>
          </div>
        </div>
      );
    };

    return (
      <div>
        <HomeSplash siteConfig={siteConfig} language={language} />
        <div className="mainContainer">
          {/* <FeatureCallout /> */}
          {/* <Features /> */}
          <BigFeature1/>
          <BigFeature2/>
          <BigFeature3/>
          {/* <Description /> */}
          {/* <Showcase /> */}
        </div>
      </div>
    );
  }
}

module.exports = Index;
