const OrganChain = artifacts.require("OrganChain"); // or OrganDonorChain if file named that

module.exports = function (deployer) {
  deployer.deploy(OrganChain);
};