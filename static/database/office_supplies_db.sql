-- phpMyAdmin SQL Dump
-- version 5.1.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Feb 16, 2026 at 06:51 AM
-- Server version: 5.7.24
-- PHP Version: 8.3.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `office_supplies_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `first_name`, `last_name`, `email`, `password`, `created_at`) VALUES
(1, 'admin', 'Saira Mae', 'Necosia', 'admin@example.com', 'Saira_157Mae', '2026-02-13 08:35:36');

-- --------------------------------------------------------

--
-- Table structure for table `inventory`
--

CREATE TABLE `inventory` (
  `id` int(11) NOT NULL,
  `item_name` varchar(255) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `stock_quantity` int(11) DEFAULT '0',
  `unit` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `inventory`
--

INSERT INTO `inventory` (`id`, `item_name`, `category`, `stock_quantity`, `unit`, `created_at`, `updated_at`) VALUES
(1, 'Stiky Note 3X3 ', 'Stationery Supplies', 20, 'Pcs', '2026-02-16 01:30:50', '2026-02-16 01:56:22'),
(2, 'Bond Paper A4', 'Paper Products', 25, 'Ream', '2026-02-16 01:37:22', '2026-02-16 02:29:27'),
(3, 'Tissue ', 'Office Essentials', 22, 'Pcs', '2026-02-16 01:57:21', '2026-02-16 02:29:27'),
(4, 'Titus Ballpen', 'Writing Instruments', 10, 'Pcs', '2026-02-16 06:30:59', '2026-02-16 06:30:59'),
(5, 'Staple Wire ', 'Stationery Supplies', 2, 'Box', '2026-02-16 06:33:31', '2026-02-16 06:33:31'),
(6, 'Stapler ', 'Stationery Supplies', 1, 'Pcs', '2026-02-16 06:34:35', '2026-02-16 06:34:35'),
(7, 'Folder White Long', 'Paper Products', 17, 'Pcs', '2026-02-16 06:35:07', '2026-02-16 06:35:07'),
(8, 'Paper Clip Metal Small', 'Stationery Supplies', 20, 'Pcs', '2026-02-16 06:35:50', '2026-02-16 06:35:50'),
(9, 'MyGel Pen Black .5', 'Writing Instruments', 28, 'Pcs', '2026-02-16 06:37:13', '2026-02-16 06:37:13'),
(10, 'MyGel Pen Blue .5', 'Writing Instruments', 28, 'Pcs', '2026-02-16 06:37:53', '2026-02-16 06:37:53'),
(11, 'log Book (150 pages)', 'Office Paper Products', 30, 'Pcs', '2026-02-16 06:43:16', '2026-02-16 06:43:16'),
(12, 'expanded Folder long', 'Office Paper Products', 50, 'Pcs', '2026-02-16 06:44:47', '2026-02-16 06:44:47'),
(13, 'Expanded Folder Ordinary', 'Office Paper Products', 50, 'Pcs', '2026-02-16 06:46:22', '2026-02-16 06:46:22');

-- --------------------------------------------------------

--
-- Table structure for table `requests`
--

CREATE TABLE `requests` (
  `id` int(11) NOT NULL,
  `mrs_no` varchar(50) NOT NULL,
  `department` varchar(100) DEFAULT NULL,
  `request_date` date DEFAULT NULL,
  `status` varchar(50) DEFAULT 'Pending',
  `requester_name` varchar(255) DEFAULT NULL,
  `requester_position` varchar(100) DEFAULT NULL,
  `requester_date` date DEFAULT NULL,
  `approver_name` varchar(255) DEFAULT NULL,
  `approver_position` varchar(100) DEFAULT NULL,
  `approver_date` date DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `request_items`
--

CREATE TABLE `request_items` (
  `id` int(11) NOT NULL,
  `request_id` int(11) NOT NULL,
  `item_description` varchar(255) NOT NULL,
  `quantity` int(11) NOT NULL,
  `unit` varchar(50) DEFAULT NULL,
  `purpose` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `inventory`
--
ALTER TABLE `inventory`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `requests`
--
ALTER TABLE `requests`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `mrs_no` (`mrs_no`);

--
-- Indexes for table `request_items`
--
ALTER TABLE `request_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `request_id` (`request_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `inventory`
--
ALTER TABLE `inventory`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `requests`
--
ALTER TABLE `requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `request_items`
--
ALTER TABLE `request_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `request_items`
--
ALTER TABLE `request_items`
  ADD CONSTRAINT `request_items_ibfk_1` FOREIGN KEY (`request_id`) REFERENCES `requests` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
