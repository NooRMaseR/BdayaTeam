import { gql } from "@apollo/client";
import { print } from "graphql";

export const GET_SITE_IMAGE_SETTINGS = print(gql`
  query settingsSiteImage {
    allSettings {
      siteImage
    }
  }
`);

export const GET_HERO_IMAGE_SETTINGS = print(gql`
  query settingsHeroImage {
    allSettings {
      heroImage
    }
  }
`);

export const GET_IMAGES_SETTINGS = print(gql`
  query settingsImages {
    allSettings {
      siteImage
      heroImage
    }
  }
`);

export const EDITABLE_FIELDS = print(gql`
    query SeeOrganizerCanEdit {
      allSettings {
        organizerCanEdit
      }
    }
`);

export const GET_ALL_SETTINGS = print(gql`
    query GetAllSettings{
      allSettings {
        siteImage
        heroImage
        isRegisterEnabled
        organizerCanEdit
      }
    }
`);

export const CAN_REGISTER = print(gql`
  query SeeCanRegister{
    canRegister
  }
`);

export const GET_TRACK_IMAGE = print(gql`
  query get_track_image($track: String) {
    track(track: $track) {
      image
    }
  }
`);

export const GET_MEMBER_CODE = print(gql`
  query get_member_code {
    member {
      code
    }
  }
`);
