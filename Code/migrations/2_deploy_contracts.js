const Satellites = artifacts.require("Satellites");

module.exports = function (deployer) {
  deployer.deploy(Satellites);
};
